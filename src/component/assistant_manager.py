import time
from src.base.function_base import ChatMessage


class AssistantManager:
    def __init__(self, context):
        self._context = context
        self._assistant = self._create_assistant()

    def _create_assistant(self):
        config = self._context.get_config()
        client = self._context.get_client()
        assistant_id = config.get("assistant_id")
        model = config.get("summary_model")
        if assistant_id is not None:
            assistants_list = client.beta.assistants.list(limit=100)
            for assistant in assistants_list:
                if assistant.id == assistant_id:
                    return assistant
        else:
            assistant = client.beta.assistants.create(
                model=model,
            )
            self._context.update_config({"assistant_id": assistant.id})
            return assistant

    def update_assistant_with_vector_stores(self, vector_store_ids: list):
        config = self._context.get_config()
        client = self._context.get_client()
        prompt = config.get("summary_prompt")
        model = config.get("summary_model")
        client.beta.assistants.update(
            assistant_id=self._assistant.id,
            name="Summary paper assistant",
            instructions=prompt,
            model=model,
            tools=[{
                "type": "file_search",
            }],
            tool_resources={
                "file_search": {
                    "vector_store_ids": vector_store_ids
                }
            },
        )

    def chat_with_message(self, message: str):
        client = self._context.get_client()
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message,
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self._assistant.id,
        )
        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=run.thread_id,
                run_id=run.id,
            )
            time.sleep(0.5)

        response = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
        return ChatMessage(role="assistant", content=response.data[1].content[0].text)
