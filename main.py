from peer_node import run_node

if __name__ == "__main__":
    # Configuración de los nodos
    nodes = [
        {"ip": "127.0.0.1", "port": 5000, "grpc_port": 50051, "directory": "C:/Users/USUARIO/OneDrive/Escritorio/P2P_CHORD_SYSTEM/nodes_directory/node 1", "bootstrap_peer": None},
        {"ip": "127.0.0.1", "port": 5001, "grpc_port": 50052, "directory": "C:/Users/USUARIO/OneDrive/Escritorio/P2P_CHORD_SYSTEM/nodes_directory/node 2", "bootstrap_peer": "127.0.0.1:5000"},
        {"ip": "127.0.0.1", "port": 5002, "grpc_port": 50053, "directory": "C:/Users/USUARIO/OneDrive/Escritorio/P2P_CHORD_SYSTEM/nodes_directory/node 3", "bootstrap_peer": "127.0.0.1:5000"},
        {"ip": "127.0.0.1", "port": 5003, "grpc_port": 50054, "directory": "C:/Users/USUARIO/OneDrive/Escritorio/P2P_CHORD_SYSTEM/nodes_directory/node 4", "bootstrap_peer": "127.0.0.1:5000"},
    ]

    # Iniciar los nodos en procesos separados
    from multiprocessing import Process

    processes = []
    for node in nodes:
        p = Process(target=run_node, args=(node["ip"], node["port"], node["grpc_port"], node["directory"], node["bootstrap_peer"]))
        processes.append(p)
        p.start()

    # Esperar a que todos los procesos finalicen
    for p in processes:
        p.join()
