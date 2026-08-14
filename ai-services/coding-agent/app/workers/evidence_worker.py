import pika
import json
import os
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "coding.events.ai_evaluation_completed"

def build_faculty_evidence(submission_id, data):
    print(f"[EvidenceBuilder] Compiling Final Assessment Report for {submission_id}...")
    time.sleep(1.5) # Mock compilation time
    
    # This data would be sent to the FacultyIQ Decision Agent
    print(f"[EvidenceBuilder] Success! Generated robust faculty evidence payload.")
    
def callback(ch, method, properties, body):
    data = json.loads(body)
    submission_id = data.get("SubmissionId")
    print(f"[EvidenceBuilder] Received AiEvaluationCompletedEvent for: {submission_id}")
    
    # Feed data into the Final Assessment Report for the Decision Agent.
    build_faculty_evidence(submission_id, data)
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.exchange_declare(exchange='coding.events', exchange_type='topic')
    channel.queue_declare(queue=QUEUE_NAME)
    # The AI worker publishes to routing key ai_evaluation.completed
    channel.queue_bind(exchange='coding.events', queue=QUEUE_NAME, routing_key='ai_evaluation.completed')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print('[EvidenceBuilder] Waiting for AI Evaluation results. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()
