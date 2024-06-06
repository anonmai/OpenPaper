import os
import time
from src.component.context import Context


class FileManager:
    def __init__(self, context):
        self._context = context

    def find_file_id(self, file_path) -> str or None:
        client = self._context.get_client()
        files = client.files.list()
        file_name = os.path.split(file_path)[1]
        for file in files:
            if file.filename == file_name:
                return file.id

    def upload_files(self, paths: set, unique_id: str):
        client = self._context.get_client()

        def filter_path(abs_path):
            if self.find_file_id(abs_path) is None:
                return True
            return False
        # 找到所有已经存在的vector store，然后从中找到这次要用的那个
        vector_store_list = client.beta.vector_stores.list()
        vector_store = None
        for vs in vector_store_list:
            if vs.name == unique_id:
                vector_store = vs
        # 如果不存在vector store,则创建一个
        if not vector_store:
            vector_store = client.beta.vector_stores.create(name=f"{unique_id}")

        # 已经在vector store中的文件列表
        stored_files = client.beta.vector_stores.files.list(vector_store.id, limit=100)
        # 删除其中所有的文件引用和实际远端的文件
        for stored_file in stored_files:
            client.beta.vector_stores.files.delete(vector_store_id=vector_store.id, file_id=stored_file.id)
            client.files.delete(file_id=stored_file.id)
        # 需要上传的文件列表
        upload_files = {path for path in paths if filter_path(path)}
        uploaded_files = paths - upload_files
        print(f"列表中需要上传的文件为：\n{paths}")
        print(f"实际上传的文件为：\n{upload_files}")
        # 所有需要上传的文件
        file_streams = [open(path, "rb") for path in upload_files]
        # 已经上传过的文件，远端仍然保留着的不用上传
        uploaded_ids = [self.find_file_id(path) for path in uploaded_files]
        # 上传文件
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams, file_ids=uploaded_ids
        )
        while file_batch.status != "completed":
            if file_batch.status != "in_progress":
                raise Exception(f"error: 上传文件过程出错，file_batch.status = {file_batch.status}, vector_store_id = {vector_store.id}")
            time.sleep(0.5)

        return vector_store

    def delete_all_vector_stores(self):
        """
        删除所有vector store
        :return:
        """
        client = self._context.get_client()
        vector_store_list = client.beta.vector_stores.list()
        for vs in vector_store_list:
            client.beta.vector_stores.delete(vector_store_id=vs.id)

    def delete_all_files(self):
        """
        删除所有的远端文件
        :return:
        """
        client = self._context.get_client()
        files = client.files.list()
        for file in files:
            client.files.delete(file_id=file.id)


if __name__ == '__main__':
    # client = get_base_client()
    context = Context("./config.yml")
    file_manager = FileManager(context)
    vs = file_manager.upload_files(paths={
        "./demo.txt",
        "./story1111.txt",
    }, unique_id="demotest")


