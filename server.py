import uvicorn
from fastapi import FastAPI
from microservices.index_service import IndexService
from microservices.upload_service import UploadService
from microservices.download_service import DownloadService
from microservices.dht_service_grpc import serve as grpc_serve
from multiprocessing import Process
from mom_producer import send_message

app = FastAPI()

# Registrar microservicios REST
app.include_router(IndexService.router)
app.include_router(UploadService.router)
app.include_router(DownloadService.router)

def run_rest():
    uvicorn.run(app, host="127.0.0.1", port=5000)

def run_grpc():
    grpc_serve()

def run_mom():
    send_message("Nodo inicializado")

if __name__ == "__main__":
    rest_process = Process(target=run_rest)
    grpc_process = Process(target=run_grpc)
    mom_process = Process(target=run_mom)

    # Iniciar todos los procesos
    rest_process.start()
    grpc_process.start()
    mom_process.start()

    rest_process.join()
    grpc_process.join()
    mom_process.join()
