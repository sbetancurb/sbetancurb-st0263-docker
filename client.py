import os
import requests

class P2PClient:
    def __init__(self):
        self.portmapper_url = "http://127.0.0.1:8000"
        self.client_directory = "./cliente_archivos"
        if not os.path.exists(self.client_directory):
            os.makedirs(self.client_directory)

    def search_file(self, filename):
        try:
            response = requests.get(f"{self.portmapper_url}/search/{filename}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "node_address" in data:
                    node_address = data["node_address"]
                    print(f"El archivo '{filename}' se encuentra en el nodo: {node_address}")

                    download_choice = input(f"¿Quieres descargar el archivo '{filename}' desde {node_address}? (s/n): ").strip().lower()
                    if download_choice == 's':
                        self.download_file(node_address, filename)
                    else:
                        print("Descarga cancelada.")
                elif isinstance(data, str):
                    print(data)  # Muestra el mensaje que indica que la petición fue encolada.
                else:
                    print(f"Error inesperado en la respuesta: {data}")
            else:
                print(f"Error al buscar el archivo: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error al conectar con el portmapper: {e}")

    def download_file(self, node_address, filename):
        try:
            response = requests.get(f"http://{node_address}/download/{filename}")
            if response.status_code == 200:
                save_path = os.path.join(self.client_directory, filename)
                with open(save_path, "wb") as file:
                    file.write(response.content)
                print(f"Archivo '{filename}' descargado con éxito y guardado en '{save_path}'.")
            else:
                print(f"Error al descargar el archivo: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error al descargar el archivo: {e}")

    def upload_file(self, file_path, node_address):
        try:
            with open(file_path, "rb") as file:
                files = {"file": (file_path.split("/")[-1], file.read())}
                data = {"node_address": node_address}
                response = requests.post(f"{self.portmapper_url}/upload/", files=files, data=data)
                if response.status_code == 200:
                    print(response.json()["message"])
                else:
                    print(f"Error al subir el archivo: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error al subir el archivo: {e}")

    def get_all_nodes(self):
        try:
            response = requests.get(f"{self.portmapper_url}/all_nodes")
            if response.status_code == 200:
                nodes_data = response.json()
                all_nodes = nodes_data["all_nodes"]
                active_nodes = nodes_data["active_nodes"]

                print("Nodos disponibles en la red (activos e inactivos):")
                for node in all_nodes:
                    status = "Activo" if node in active_nodes else "Inactivo"
                    print(f"- {node} ({status})")
                return all_nodes
            else:
                print(f"Error al obtener la lista de nodos: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error al conectar con el portmapper: {e}")
            return []

if __name__ == "__main__":
    client = P2PClient()

    while True:
        print("\nOpciones:")
        print("1. Buscar y descargar un archivo")
        print("2. Subir un archivo")
        print("3. Ver todos los nodos")
        print("4. Salir")

        choice = input("Selecciona una opción: ")

        if choice == "1":
            filename = input("Ingresa el nombre del archivo que deseas buscar: ")
            client.search_file(filename)
        elif choice == "2":
            all_nodes = client.get_all_nodes()  # Obtener todos los nodos registrados
            if all_nodes:
                file_path = input("Ingresa la ruta del archivo que deseas subir: ")
                print("Selecciona el nodo al que deseas subir el archivo:")
                for idx, node in enumerate(all_nodes, start=1):
                    print(f"{idx}. {node}")
                node_choice = int(input("Ingresa el número del nodo: "))
                if 1 <= node_choice <= len(all_nodes):
                    node_address = all_nodes[node_choice - 1]
                    client.upload_file(file_path, node_address)
                else:
                    print("Opción de nodo no válida.")
            else:
                print("No hay nodos disponibles para subir archivos.")
        elif choice == "3":
            client.get_all_nodes()
        elif choice == "4":
            print("Saliendo...")
            break
        else:
            print("Opción no válida, por favor intenta de nuevo.")
