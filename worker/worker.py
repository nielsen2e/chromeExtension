import pika

def callback(ch, method, properties, body):
    filepath = body.decode()
    print(f" [x] Received {filepath}")
    # Here you would add the logic to transcribe the video at filepath.
    # For this prototype, we're just printing the received file path.

# Setup RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='transcribe')

channel.basic_consume(queue='transcribe', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
