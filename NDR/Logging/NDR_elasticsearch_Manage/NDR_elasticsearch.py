from elasticsearch import Elasticsearch

from Logging.NDR_elasticsearch_Manage.elasticsearch_json import index_patterns, index_name
from Logging.NDR_elasticsearch_Manage.elasticsearch_json import NDR_categorical_component_template_name, NDR_categorical_component_template
from Logging.NDR_elasticsearch_Manage.elasticsearch_json import template_name, template


class NDR_Elasticsearch():
    def __init__(
        self,
        ElasticSearch_IP:str,
        ElasticSearch_PORT:int,
        INDEX_PATTERN:str = index_patterns,
    ):
        self.es = Elasticsearch(hosts=[f"http://{ElasticSearch_IP}:{ElasticSearch_PORT}"])
        self.INDEX_PATTERN = INDEX_PATTERN
        self.indexName = index_name
        
        # NDR Categorical 체크
        self.check_NDR_Categorical()
        
        # NDR Unique - index template 체크
        self.check_NDR_index_template()
        
        
    
    
    
    def check_NDR_Categorical(self):
        
        if not self.es.cluster.exists_component_template(
            name= NDR_categorical_component_template_name
        ):
            print("NDR 카테고리 컴포넌트가 없어, 생성합니다.")
            self.es.cluster.put_component_template(
                name= NDR_categorical_component_template_name,
                body= NDR_categorical_component_template,
            )
            
    def check_NDR_index_template(self):
        
        if not self.es.indices.exists_index_template(
            name = template_name
        ):
            print("NDR 인덱스 템플릿 없으므로 생성")
            self.es.indices.put_index_template(
                name = template_name,
                body = template
            )
        else:
            print("NDR 인덱스 템플릿 이미 존재함")