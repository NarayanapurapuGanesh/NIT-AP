import pika
import json
import os
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "coding.events.static_analysis_completed"

def evaluate_with_qwen(submission_id):
    # This is a stub for the Ollama integration
    # e.g., requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5-coder:3b", ...})
    print(f"[AI-Worker] Prompting Qwen2.5-Coder for submission {submission_id}...")
    time.sleep(2) # Mock inference time
    
    return {
        "TeachingQualityScore": 88.5,
        "InterviewReadinessScore": 92.0,
        "OptimizationSuggestions": "Consider using a hash map to reduce time complexity from O(n^2) to O(n).",
        "FollowUpQuestions": [
            "What happens to the memory usage if the array size is 10^9?",
            "Can you explain the trade-offs of using a hash map here?"
        ]
    }

def callback(ch, method, properties, body):
    data = json.loads(body)
    submission_id = data.get("SubmissionId")
    print(f"[AI-Worker] Received StaticAnalysisCompletedEvent for: {submission_id}")
    
    # Run Ollama AI Evaluation
    evaluation = evaluate_with_qwen(submission_id)
    
    ai_event = {
        "SubmissionId": submission_id,
        "TeachingQualityScore": evaluation["TeachingQualityScore"],
        "InterviewReadinessScore": evaluation["InterviewReadinessScore"],
        "OptimizationSuggestions": evaluation["OptimizationSuggestions"],
        "FollowUpQuestions": evaluation["FollowUpQuestions"]
    }
    
    ch.basic_publish(
        exchange='coding.events',
        routing_key='ai_evaluation.completed',
        body=json.dumps(ai_event)
    )
    
    print(f"[AI-Worker] Published AiEvaluationCompletedEvent for {submission_id}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.exchange_declare(exchange='coding.events', exchange_type='topic')
    channel.queue_declare(queue=QUEUE_NAME)
    # The static analysis worker publishes to routing key static_analysis.completed
    channel.queue_bind(exchange='coding.events', queue=QUEUE_NAME, routing_key='static_analysis.completed')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print('[AI-Worker] Waiting for static analysis results. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()
