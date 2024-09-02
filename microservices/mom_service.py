import pika

class MOMService:
    def __init__(self, node_address=None):
        self.node_address = node_address
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()
            if self.node_address:
                self.channel.queue_declare(queue=self.node_address, durable=True)
            print(f"Conexión con RabbitMQ establecida y cola '{self.node_address}' declarada.")

        except Exception as e:
            print(f"Error al conectar con RabbitMQ: {e}")

    def send_message(self, message, queue_name=None):
        if queue_name is None:
            queue_name = self.node_address
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # hacer el mensaje persistente
                )
            )
            print(f" [x] Sent '{message}' to queue '{queue_name}'")
        except Exception as e:
            print(f"Error al enviar el mensaje: {e}")

    def consume_messages(self, callback):
        try:
            self.channel.basic_consume(
                queue=self.node_address,
                on_message_callback=lambda ch, method, properties, body: callback(eval(body.decode())),
                auto_ack=True
            )
            print(f" [*] Waiting for messages on queue '{self.node_address}'. To exit press CTRL+C")
            self.channel.start_consuming()
        except Exception as e:
            print(f"Error al consumir mensajes: {e}")

    def close(self):
        try:
            self.connection.close()
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")
