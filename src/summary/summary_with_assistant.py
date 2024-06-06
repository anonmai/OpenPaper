from ..base.function_base import ChatMessage
import threading
from src.component.file_manager import FileManager
from src.component.context import Context
from src.component.assistant_manager import AssistantManager
import sys
import time


class SummaryPaperAssistant:
    def summary(self) -> (ChatMessage, bool):
        self._is_running = True
        loading_thread = threading.Thread(target=self.start_waiting_animation, args=("summarizing",))
        loading_thread.start()
        # 获得config
        config = self._context.get_config()

        conversation = config.get("is_conversation")
        message = config.get("message")
        if not conversation:
            # 如果不是对话，则完全更新assistant
            files = set(config.get("files"))
            unique_id = config.get("unique_id")
            # 获得vector_store
            vector_store = self._file_manager.upload_files(files, unique_id)
            # 更新assistant,与文件关联起来
            self._assistant_manager.update_assistant_with_vector_stores(vector_store_ids=[vector_store.id])
        chat_message = self._assistant_manager.chat_with_message(message)
        self._is_running = False
        loading_thread.join()
        return chat_message

    def __init__(self, context: Context):
        super().__init__()
        self._is_running = None
        self._context = context
        self._file_manager = FileManager(self._context)
        self._assistant_manager = AssistantManager(self._context)

    def start_waiting_animation(self, do: str):
        animation = ["...|", ".../", "...—", "...\\"]
        i = 0
        while self._is_running:
            i += 1
            i %= len(animation)
            sys.stdout.write("\r" + f"{do} {self.function_name()}" + animation[i])
            sys.stdout.flush()
            time.sleep(0.3)

        sys.stdout.write("\r" + f"{self.function_name()} Complete!\n")

    def function_name(self):
        return "summary_paper"


if __name__ == '__main__':
    context = Context("./config.yml")
    summary_paper_assistant = SummaryPaperAssistant(context)
    summary = summary_paper_assistant.summary()
    print(summary)


