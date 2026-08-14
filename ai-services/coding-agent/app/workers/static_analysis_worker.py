import pika
import json
import os
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "coding.events.execution_completed"

def callback(ch, method, properties, body):
    data = json.loads(body)
    submission_id = data.get("SubmissionId")
    print(f"[StaticAnalysis] Received ExecutionCompletedEvent for: {submission_id}")
    
    # In a real setup, we would fetch the code from PostgreSQL or passed via the event
    # and use radon or flake8 to analyze it.
    print(f"[StaticAnalysis] Running cyclomatic complexity & maintainability index...")
    time.sleep(1) # Mock processing
    
    analysis_event = {
        "SubmissionId": submission_id,
        "CyclomaticComplexity": 12,
        "MaintainabilityIndex": 85.5,
        "DuplicateLines": 0
    }
    
    ch.basic_publish(
        exchange='coding.events',
        routing_key='static_analysis.completed',
        body=json.dumps(analysis_event)
    )
    
    print(f"[StaticAnalysis] Published StaticAnalysisCompletedEvent for {submission_id}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.exchange_declare(exchange='coding.events', exchange_type='topic')
    channel.queue_declare(queue=QUEUE_NAME)
    # The sandbox worker publishes to routing key execution.completed
    channel.queue_bind(exchange='coding.events', queue=QUEUE_NAME, routing_key='execution.completed')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print('[StaticAnalysis] Waiting for execution results. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()
