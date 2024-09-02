from fastapi import APIRouter
import os

class IndexService:
    def __init__(self, directory):
        self.router = APIRouter()
        self.directory = directory

        @self.router.get("/index")
        def list_files():
            files = os.listdir(self.directory)
            file_list = [{"filename": f, "path": f"{self.directory}/{f}"} for f in files]
            return {"files": file_list}
