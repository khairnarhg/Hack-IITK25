from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='host.docker.internal:9092')
print("Kafka connected!")
