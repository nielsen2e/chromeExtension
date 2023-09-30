import os
import uuid
from flask import request, jsonify
import pika
from app import app

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

# Ensure the UPLOAD_FOLDER exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Setup RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='transcribe')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.data
    file_id = str(uuid.uuid4())
    if not file:
        return 'No file received', 400

    filename = f"{file_id}.mp4"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Write the binary data to a file on the disk
    with open(filepath, 'wb') as f:
        f.write(file)

    # Send message to RabbitMQ for background transcription
    channel.basic_publish(exchange='', routing_key='transcribe', body=filepath)

    return jsonify({"id": file_id, "url": f"/videos/{filename}"}), 200
