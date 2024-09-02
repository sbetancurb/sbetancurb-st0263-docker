import uvicorn
from fastapi import FastAPI
from multiprocessing import Process
from microservices.index_service import IndexService
from microservices.upload_service import UploadService
from microservices.download_service import DownloadService
from microservices.dht_service_grpc import serve as grpc_serve
from microservices.mom_service import MOMService
import requests

class PeerNode:
    def __init__(self, ip: str, port: int, grpc_port: int, directory: str, bootstrap_peer: str = None):
        self.ip = ip
        self.port = port
        self.directory = directory
        self.grpc_port = grpc_port
        self.bootstrap_peer = bootstrap_peer
        self.node_address = f"{self.ip}:{self.port}"

    def run_rest(self):
        # Crear la aplicación FastAPI dentro del proceso para evitar problemas de serialización
        app = FastAPI()

        # Registrar microservicios REST
        app.include_router(IndexService(self.directory).router)
        app.include_router(UploadService(self.directory).router)
        app.include_router(DownloadService(self.directory).router)

        uvicorn.run(app, host=self.ip, port=self.port)

    def run_grpc(self):
        grpc_serve(self.grpc_port)

    def run_mom(self):
        mom_service = MOMService(self.node_address)
        mom_service.consume_messages(callback=self.process_mom_messages)

    def process_mom_messages(self, message):
        task_type = message.get("task_type")
        filename = message.get("filename")
        file_content = message.get("file_content")

        if task_type == "upload":
            print(f"Procesando la subida de archivo '{filename}' desde la cola.")
            files = {"file": (filename, file_content)}
            response = requests.post(f"http://{self.node_address}/upload/", files=files)
            if response.status_code == 200:
                print(f"Archivo '{filename}' subido con éxito.")
            else:
                print(f"Error al subir el archivo desde la cola: {response.status_code} - {response.text}")
        else:
            print(f"Tarea no reconocida: {task_type}")

    def run_all_services(self):
        rest_process = Process(target=self.run_rest)
        grpc_process = Process(target=self.run_grpc)
        mom_process = Process(target=self.run_mom)

        # Iniciar todos los procesos
        rest_process.start()
        grpc_process.start()
        mom_process.start()

        rest_process.join()
        grpc_process.join()
        mom_process.join()

def run_node(ip, port, grpc_port, directory, bootstrap_peer=None):
    node = PeerNode(ip=ip, port=port, grpc_port=grpc_port, directory=directory, bootstrap_peer=bootstrap_peer)
    node.run_all_services()
