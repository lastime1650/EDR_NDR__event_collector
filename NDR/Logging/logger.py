

class Logger():
    def __init__(
        self,
        
        KAFKA_IP:str="kafka",
        KAFKA_PORT:int=9092,
        ElasticSearch_IP:str="elasticsearch",
        ElasticSearch_PORT:int=9200,
    ):
        # 엘라스틱서치 객체
        from Logging.NDR_elasticsearch_Manage.NDR_elasticsearch import NDR_Elasticsearch
        self.NDR_ElasticSearch = NDR_Elasticsearch(
            ElasticSearch_IP=ElasticSearch_IP,
            ElasticSearch_PORT=ElasticSearch_PORT
        )
        
        # Kafka 객체
        from Logging.kafka.NDR_kafka import NDR_Kafka
        self.NDR_Kafka = NDR_Kafka(
            KAFKA_IP=KAFKA_IP,
            KAFKA_PORT=KAFKA_PORT,
            Topic=self.NDR_ElasticSearch.indexName # 엘라스틱서치 인덱스이름 
        )
        
        
    def Send_Log(self, data:dict):
        # 엘라스틱서치에 필요한 데이터를 인자로 받고
        
        # Kafka 전송
        self.NDR_Kafka.Send(
            msg=data
        )