from src.base.function_base import FunctionBase, ChatMessage
from serpapi.google_search import GoogleSearch
import threading

# 输入谷歌学术的API key
google_scholar_apikey = ""

def reformat_title(text: str) -> str:
    return '_'.join(text.split())


class SearchPaperFunction(FunctionBase):
    def function_description(self) -> str:
        return """This function is used to search for papers on Google Scholar"""

    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": f"""
                            Parameter defines the query you want to search. 
                            You can also use helpers in your query such as: author:, or source:.
                            Usage of cites parameter makes q optional. 
                            Usage of cites together with q triggers search within citing articles.
                            """,
                },
                "num": {
                    "type": "integer",
                    "description": f"""
                                    Parameter defines the maximum number of results to return, limited to 20. (e.g., 10 (default) returns 10 results, 20 returns 20 results).
                                    """,
                },
                "cites": {
                    "type": "string",
                    "description": f"""
                                    Parameter defines unique ID for an article to trigger Cited By searches. 
                                    Usage of cites will bring up a list of citing documents in Google Scholar. 
                                    Example value: cites=1275980731835430123. Usage of cites and q parameters triggers search within citing articles.
                                    """,
                }
            },
            "required": ["q"]
        }

    def exec(self, args) -> (ChatMessage, bool):
        self.is_running = True
        loading_thread = threading.Thread(target=self.start_waiting_animation, args=("searching",))
        loading_thread.start()
        q = args.get("q")
        cites = args.get("cites")
        num = args.get("num")
        chat_message = self.search_paper(
                            q=q,
                            cites=cites,
                            num=num,)
        self.is_running = False
        loading_thread.join()
        return chat_message, True

    def function_name(self) -> str:
        return "search_paper"

    def result(self) -> dict:
        return {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": """This is the Information of a paper，
                    There are three string in the array, 
                    the first is the title of the paper, 
                    the second is the snippet of the paper, 
                    the third is a paper download link"""
                }
            },
            "description": "Information about the number of articles searched using the num parameter"
        }

    def search_paper(self, q: str, **kwargs):
        normal_params = {
            "engine": "google_scholar",
            "q": q,
            "api_key": google_scholar_apikey,
        }
        normal_params.update(kwargs)

        search = GoogleSearch(normal_params)
        results = search.get_dict()
        organic_results = results["organic_results"]

        papers = []
        # 这里是下载文章
        for item in organic_results:
            if item.get('resources'):
                # 文章标题
                title = reformat_title(item['title'])
                # 文章总结
                snippet = item['snippet']
                # 文章pdf的下载url
                url = item['resources'][0]['link']
                papers.append([title, snippet, url])

        role = "function"
        content = str(papers)
        return ChatMessage(role, content, self.function_name())


if __name__ == '__main__':
    # 如何搜索和下载paper的pdf文件

    # 关键字
    key_words = 'transformer'

    # 下载数量
    paper_num = 10
    # 从google学术上搜索论文信息
    search_paper = SearchPaperFunction()
    search_paper.exec(q=key_words, num=3)
