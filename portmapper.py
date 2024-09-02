from fastapi import FastAPI, HTTPException, UploadFile, Form
import requests
import pika
import json

app = FastAPI()

# Lista de nodos en la red
NODES = [
    "127.0.0.1:5000",
    "127.0.0.1:5001",
    "127.0.0.1:5002",
    "127.0.0.1:5003"
]

def check_active_nodes():
    active_nodes = []
    for node in NODES:
        try:
            response = requests.get(f"http://{node}/index", timeout=2)
            if response.status_code == 200:
                active_nodes.append(node)
                # Si el nodo está activo, procesar las peticiones en cola
                process_queued_requests_for_node(node)
        except requests.exceptions.RequestException:
            continue
    return active_nodes

def process_queued_requests_for_node(node):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=node, durable=True)

        while True:
            method_frame, header_frame, body = channel.basic_get(queue=node, auto_ack=True)
            if method_frame:
                request = json.loads(body.decode())
                task_type = request['task_type']
                filename = request.get('filename')
                file_content = request.get('file_content').encode('utf-8') if request.get('file_content') else None

                if task_type == "upload" and file_content:
                    try:
                        files = {"file": (filename, file_content)}
                        response = requests.post(f"http://{node}/upload/", files=files)
                        if response.status_code == 200:
                            print(f"Archivo '{filename}' subido con éxito al nodo {node} desde la cola.")
                        else:
                            print(f"Error al subir el archivo desde la cola: {response.status_code} - {response.text}")
                    except Exception as e:
                        print(f"Error al subir el archivo desde la cola: {e}")
                elif task_type == "search":
                    # Lógica para procesar una búsqueda desde la cola, si fuera necesario
                    pass
            else:
                break

        connection.close()
    except Exception as e:
        print(f"Error al procesar las peticiones en cola para el nodo {node}: {e}")

def is_node_active(node_address):
    try:
        response = requests.get(f"http://{node_address}/index", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
    
@app.get("/all_nodes")
def get_all_nodes():
    active_nodes = check_active_nodes()
    return {"all_nodes": NODES, "active_nodes": active_nodes}


def send_to_queue(node_address, task_type, filename=None, file=None):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=node_address, durable=True)

        message = {
            "task_type": task_type,
            "filename": filename,
            "file_content": file.decode('utf-8') if file else None
        }

        channel.basic_publish(
            exchange='',
            routing_key=node_address,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # hacer el mensaje persistente
            )
        )
        connection.close()
        print(f"Mensaje encolado para el nodo {node_address}: {message}")
    except Exception as e:
        print(f"Error al enviar el mensaje a la cola: {e}")

def process_queued_requests():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        for node in NODES:
            channel.queue_declare(queue=node, durable=True)
            while True:
                method_frame, header_frame, body = channel.basic_get(queue=node, auto_ack=True)
                if method_frame:
                    request = json.loads(body.decode())
                    task_type = request['task_type']
                    filename = request.get('filename')
                    file_content = request.get('file_content').encode('utf-8') if request.get('file_content') else None

                    if is_node_active(node):
                        print(f"Procesando petición encolada para el nodo {node}")
                        send_to_queue(node, task_type, filename, file_content)
                    else:
                        # Si el nodo sigue inactivo, volver a encolar con prioridad
                        send_to_queue(node, task_type, filename, file_content)
                else:
                    break

        connection.close()
    except Exception as e:
        print(f"Error al procesar las peticiones en cola: {e}")

@app.on_event("startup")
async def startup_event():
    active_nodes = check_active_nodes()
    print(f"Nodos activos al inicio: {active_nodes}")


@app.get("/active_nodes")
def get_active_nodes():
    active_nodes = check_active_nodes()
    if active_nodes:
        return {"active_nodes": active_nodes}
    else:
        raise HTTPException(status_code=404, detail="No hay nodos activos en la red.")

def find_node_with_file(filename):
    global message
    message = None
    for node in NODES:
        if is_node_active(node):
            try:
                response = requests.get(f"http://{node}/index")
                if response.status_code == 200:
                    files = response.json().get("files", [])
                    for file in files:
                        if file['filename'] == filename:
                            return node
            except requests.exceptions.RequestException as e:
                print(f"Error al conectar con el nodo {node}: {e}")
        else:
            # Encolar la petición si el nodo no está activo
            send_to_queue(node, "search", filename= filename, file= None )
            message = f"El nodo {node} no está activo. La petición se ha encolado y será procesada cuando el nodo vuelva a estar disponible."
    return None

@app.get("/search/{filename}")
def search_file(filename: str):
    # Buscar el nodo que tiene el archivo
    node_address = find_node_with_file(filename)
    if node_address in NODES:
        return {"node_address": node_address, "filename": filename}
    else:
        if message is None:
            raise HTTPException(status_code=404, detail="Archivo no encontrado en la red.")
        else:
            return message


@app.post("/upload/")
async def upload_file(file: UploadFile, node_address: str = Form(...)):
    if node_address not in NODES:
        raise HTTPException(status_code=400, detail="Nodo no válido.")

    file_content = file.file.read()

    if is_node_active(node_address):
        try:
            files = {"file": (file.filename, file_content)}
            response = requests.post(f"http://{node_address}/upload/", files=files)
            if response.status_code == 200:
                return {"message": "Archivo subido con éxito"}
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al subir el archivo: {str(e)}")
    else:
        # Encolar la petición si el nodo no está activo
        send_to_queue(node_address, "upload", filename=file.filename, file=file_content)
        return {"message": f"El nodo {node_address} no está activo. La petición se ha encolado y será procesada cuando el nodo vuelva a estar disponible."}

