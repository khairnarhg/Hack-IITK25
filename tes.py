from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')
producer.send('test-topic', b'Hello from Python!')
producer.flush()
print("Message sent!")
