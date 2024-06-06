from termcolor import colored


class Conversation:
    """
    用于记录对话
    """
    def __init__(self, history=None):
        if history is None:
            history = []
        self._conversation_history = history

    def add_message(self, message):
        self._conversation_history.append(message)

    def conversation_history(self):
        return self._conversation_history

    def pretty_print_conversation(self):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }
        for message in self._conversation_history:
            if isinstance(message, (dict, )):
                role = message["role"]
                content = message["content"]
                function_call = message.get("function_call")
                name = message.get("name")
            else:
                role = message.role
                content = message.content
                function_call = message.function_call
                name = None
            if role == "system":
                print(colored(f"system: {content}\n", role_to_color[role]))
            elif role == "user":
                print(colored(f"user: {content}\n", role_to_color[role]))
            elif role == "assistant" and function_call:
                print(colored(f"assistant: {function_call}\n", role_to_color[role]))
            elif role == "assistant" and not function_call:
                print(colored(f"assistant: {content}\n", role_to_color[role]))
            elif role == "function":
                print(colored(f"function ({name}): {content}\n", role_to_color[role]))
            pass
