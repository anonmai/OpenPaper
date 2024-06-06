from abc import ABC, abstractmethod
from dataclasses import dataclass
from openai.types.chat.chat_completion_message import ChatCompletionMessage
import sys
import time


def convert_response_to_message(chat_completion_message: ChatCompletionMessage):

    return {
        "role": chat_completion_message.role,
        "content": chat_completion_message.content,
    }


@dataclass
class ChatMessage:
    role: str
    content: str
    name: str = None

    def convert_to_message(self):
        if self.name is None:
            return {
                "role": self.role,
                "content": self.content
            }
        else:
            return {
                "role": self.role,
                "content": self.content,
                "name": self.name
            }


def chat_messages_to_json_list(chat_messages: [ChatMessage]):
    return [chat_message.convert_to_message() for chat_message in chat_messages]


class FunctionBase:
    def __init__(self):
        self.is_running = True

    @abstractmethod
    def function_description(self) -> str:
        pass

    @abstractmethod
    def parameters(self) -> dict:
        pass

    @abstractmethod
    def result(self) -> dict:
        pass

    @abstractmethod
    def exec(self, args) -> (ChatMessage, bool):
        pass

    @abstractmethod
    def function_name(self) -> str:
        pass

    def start_waiting_animation(self, do: str):
        animation = ["...|", ".../", "...—", "...\\"]
        i = 0
        while self.is_running:
            i += 1
            i %= len(animation)
            sys.stdout.write("\r" + f"{do} {self.function_name()}" + animation[i])
            sys.stdout.flush()
            time.sleep(0.3)

        sys.stdout.write("\r" + f"{self.function_name()} Complete!\n")

    def function_json_description(self) -> dict:
        return {
            "name": self.function_name(),
            "description": self.function_description(),
            "parameters": self.parameters(),
            "result": self.result()
        }
