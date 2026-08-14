import pika
import json
import docker
import time
import os
import uuid

# Connect to RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "coding.events.submit"

client = docker.from_env()

def execute_code(language, code):
    # This is a stub for the actual docker execution.
    # We would use a pre-warmed container here, e.g. python:3.11-alpine
    container_image = "python:3.11-alpine" if language == "python" else "gcc:latest"
    
    # Mocking execution delay
    time.sleep(0.5)
    
    return {
        "status": "ACCEPTED",
        "executionTimeMs": 45,
        "memoryUsageKb": 1024,
        "passedHiddenTests": 10,
        "totalHiddenTests": 10
    }

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"[*] Received Submission: {data.get('SubmissionId')}")
    
    # Run the code
    result = execute_code(data.get("Language"), data.get("Code"))
    
    # Publish ExecutionCompletedEvent
    execution_event = {
        "SubmissionId": data.get("SubmissionId"),
        "Status": result["status"],
        "ExecutionTimeMs": result["executionTimeMs"],
        "MemoryUsageKb": result["memoryUsageKb"],
        "PassedHiddenTests": result["passedHiddenTests"],
        "TotalHiddenTests": result["totalHiddenTests"]
    }
    
    ch.basic_publish(
        exchange='coding.events',
        routing_key='execution.completed',
        body=json.dumps(execution_event)
    )
    
    print(f"[*] Published ExecutionCompletedEvent for {data.get('SubmissionId')}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.exchange_declare(exchange='coding.events', exchange_type='topic')
    channel.queue_declare(queue=QUEUE_NAME)
    channel.queue_bind(exchange='coding.events', queue=QUEUE_NAME, routing_key='submit.request')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(' [*] Waiting for submissions. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    # In a real environment, we'd handle exceptions and reconnects here
    main()
