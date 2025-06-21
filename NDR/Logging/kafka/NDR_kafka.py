from kafka import KafkaProducer
import json, time

class NDR_Kafka():
    def __init__(
        self,
        KAFKA_IP:str,
        KAFKA_PORT:int,
        Topic:str
    ):
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=f"{KAFKA_IP}:{KAFKA_PORT}",
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.Topic = Topic
    
    def Send(self, msg:any):
        self.kafka_producer.send(
            topic=self.Topic,
            value=msg
        )
        #print("전송처리되었습니다.")
        time.sleep(0.1)