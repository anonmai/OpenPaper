import os.path
from src.base.function_base import FunctionBase, ChatMessage
from urllib.request import urlretrieve
import threading


def reformat_title(text: str) -> str:
    return '_'.join(text.split())


class DownloadPaperFunction(FunctionBase):
    def function_description(self) -> str:
        return """This function is used to download papers with url.
        Generally need to search papers by search_paper function first, and then download the paper by this function"""

    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": f"""
                                    title of the paper to download
                                    """,
                },
                "url": {
                    "type": "string",
                    "description": f"""
                            url of the paper to download
                            """,
                }
            },
            "required": ["title", "url"]
        }

    def exec(self, args) -> (ChatMessage, bool):
        self.is_running = True
        loading_thread = threading.Thread(target=self.start_waiting_animation, args=("downloading",))
        loading_thread.start()
        title = args.get("title")
        url = args.get("url")
        paper_dir = args.get("paper_dir", "./")
        chat_message = self.download_paper(title, url, file_dir=paper_dir)
        self.is_running = False
        loading_thread.join()
        return chat_message, True

    def function_name(self) -> str:
        return "download_paper"

    def result(self) -> dict:
        return {
            "type": "string",
            "description": "The path of the downloaded papers"
        }

    def download_paper(self, title: str, url: str, file_dir='./download_paper'):
        role = "function"
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        pdf_file = os.path.join(file_dir, f"{title}.pdf")
        try:
            # 如果已经下载过的paper，就不重复下载了
            if not os.path.exists(pdf_file):
                urlretrieve(url, pdf_file)
        except Exception as e:
            print(f'download error, url = {url}, e = {e}')
            content = "Download error, can not download this paper, do not stop, please continue the current task (for example, you can try to download another paper)"
            return ChatMessage(role, content)
        content = f"The paper has been downloaded to path:{pdf_file}"
        return ChatMessage(role, content, self.function_name())


if __name__ == '__main__':
    # 如何搜索和下载paper的pdf文件
    pass
