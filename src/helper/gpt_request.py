from tenacity import retry, wait_random_exponential, stop_after_attempt


class GPTRequest:
    @retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
    def chat_with_gpt(self, messages: list, functions=None, model=None, client=None):
        if client is None:
            raise Exception("error client is None")
        if model is None:
            model = "gpt-3.5-turbo-1106"
        if functions is not None:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                functions=functions,
                function_call="auto"
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
        return response
