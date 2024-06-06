import json
import os.path
from src.base.function_base import FunctionBase, ChatMessage, chat_messages_to_json_list
from src.helper.gpt_request import GPTRequest
from src.helper.conversation import Conversation
from src.component.context import Context
from src.download.search_paper import SearchPaperFunction
from src.download.download_paper import DownloadPaperFunction
from src.summary.summary_with_assistant import SummaryPaperAssistant
from datetime import datetime


default_content = f"""You have been asked to help me download some paper. 
    I give you some functions, search the paper by search_paper, download it by download_paper.
    Through function calls I provided to you for all operations, until you think you have answer my query
    don`t ask me any question, you make the decisions
    """


def prompt_message(prompt=default_content) -> ChatMessage:
    system_role = "system"
    system_message = ChatMessage(system_role, prompt)
    return system_message


class PaperController:
    def __init__(self,
                 conversation: Conversation,
                 call_functions: [FunctionBase],
                 gpt: GPTRequest,
                 context: Context):
        self._conversation = conversation
        self._call_functions = call_functions
        self._call_functions_dict = {}
        for function in self._call_functions:
            self._call_functions_dict.update({function.function_name(): function.exec})
        self._gpt = gpt
        self._context = context
        self._config = context.get_config()
        self._prompt_message = prompt_message()
        self._client = self._context.get_client()
        self._query = self._config.get("query")
        self._model = self._config.get("download_model")

    def register_call_function(self, function):
        self._call_functions.append(function)

    def query(self, user_query=None):
        if user_query is None:
            user_query = self._query
        prompt = self._prompt_message
        user_message = ChatMessage("user", user_query)
        self._conversation.add_message(prompt.convert_to_message())
        self._conversation.add_message(user_message.convert_to_message())
        response = self._gpt.chat_with_gpt(messages=chat_messages_to_json_list([prompt, user_message]),
                                           functions=[function.function_json_description() for function in self._call_functions],
                                           model=self._model,
                                           client=self._client)
        self.analysis_response(response)

    def keep_chat(self):
        response = self._gpt.chat_with_gpt(messages=self._conversation.conversation_history(),
                                           functions=[function.function_json_description() for function in self._call_functions],
                                           model=self._model,
                                           client=self._client)
        self.analysis_response(response)

    def analysis_response(self, response):
        response_message = response.choices[0].message
        self._conversation.add_message(response_message)
        finish_reason = response.choices[0].finish_reason
        if finish_reason == 'function_call':
            function_name = response_message.function_call.name
            function_to_call = self._call_functions_dict[function_name]
            function_args = json.loads(response_message.function_call.arguments)
            function_args.update(self._config)
            (function_message, goon) = function_to_call(function_args)
            self._conversation.add_message(function_message.convert_to_message())
            if goon:
                self.keep_chat()
            else:
                self._conversation.pretty_print_conversation()

        elif finish_reason == "stop":
            print("正常停止结束")
            self._conversation.pretty_print_conversation()
        elif finish_reason == "length":
            self._conversation.add_message(ChatMessage("user", "Go on").convert_to_message())
            self.keep_chat()
        elif finish_reason == "content_filter":
            print("触发了关键字")
            self._conversation.pretty_print_conversation()
        else:
            print("出现了错误，或者出现了一些问题")
            self.print_conversation()
            self._conversation.add_message(ChatMessage("user", "Go on").convert_to_message())
            self.keep_chat()

    def print_conversation(self):
        self._conversation.pretty_print_conversation()


def check_summary_config(summary_config: dict):
    for file in summary_config.get("files"):
        assert os.path.exists(file)

    result_file = summary_config.get("result_file")
    result_dir = os.path.split(result_file)[0]
    assert os.path.exists(result_dir)

    # model = summary_config.get("model")


if __name__ == '__main__':
    context = Context("./config.yml")
    config = context.get_config()
    if config.get("mode") == "download":
        paper_summary = PaperController(Conversation(),
                                        [SearchPaperFunction(), DownloadPaperFunction()],
                                        GPTRequest(),
                                        context)
        paper_summary.query()
    elif config.get("mode") == "summary":
        summary_paper_assistant = SummaryPaperAssistant(context)
        summary = summary_paper_assistant.summary()
        with open(config.get("result_file"), "a") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write("****************************\n")
            f.write(f"time = {now}\n")
            f.write(f"unique_id = {config.get('unique_id')}\n")
            f.write(f"files = {config.get('files')}\n")
            f.write(f"model = {config.get('summary_model')}\n")
            f.write(f"result_file = {config.get('result_file')}\n")
            f.write(f"is_conversation = {config.get('is_conversation')}\n")
            f.write(f"\n")
            f.write(f"summary:\n{summary.content.value}\n")

