import grpc
from concurrent import futures
import time
from grpc_services import dht_service_pb2_grpc, dht_service_pb2

class DHTService(dht_service_pb2_grpc.DHTServiceServicer):
    def Lookup(self, request, context):
        # Lógica para determinar el nodo responsable
        return dht_service_pb2.LookupResponse(responsible_node="127.0.0.1:5000")

def serve(grpc_port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dht_service_pb2_grpc.add_DHTServiceServicer_to_server(DHTService(), server)
    server.add_insecure_port(f'[::]:{grpc_port}')
    server.start()
    print(f"gRPC DHTService running on port {grpc_port}...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
