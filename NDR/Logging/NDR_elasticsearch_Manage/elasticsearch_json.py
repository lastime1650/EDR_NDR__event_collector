# NDR ElasticSearch 인덱스 정의

Common_component_template_name = "common_component"
Common_component_template = {
    "template": {
        "settings": {
            "number_of_shards":   1,
            "number_of_replicas": 1,
        },
        "mappings": {
            "properties": {
                "common": { 
                    "properties": {
                        "Local_Ip": {  # NDR 탐지된 Network 인터페이스 IP
                                "type": "ip",
                        },
                        "Mac_Address": { # NDR 탐지된 Network 인터페이스 IP의 MAC
                                "type": "keyword",
                        },
                        "Timestamp": {
                                "type": "date",
                        },
                    },
                },
            }
        },
        "aliases": {
                        "common_index": {},
                },
        },
        "_meta": {
                "description": "common 유형의 컴포넌트, 이 기종 간 호환되는 로그 필드",
                "version":     1,
        },
}


NDR_categorical_component_template_name = "ndr_categorical_component"
NDR_categorical_component_template = {
    "template": {
        "settings": {
            "number_of_shards":   1,
            "number_of_replicas": 1,
        },
        "mappings": {
            "properties": {
                "common": { 
                    "properties": {
                        "bound_type": {"type":"ketword"}, # 흐름 표시
                        "external_ip_info": { # 내부망과 연결된 외부망 IP 정보 
                            "properties": {
                                # 0 protocol
                                "protocol": {"type":"keyword"},
                                # 1. geoip
                                "geoip": {
                                    "properties": {
                                        "Ip": { #IP 정보
                                            "type": "ip",
                                        },
                                        "Country": { # 국가 정보
                                            "type": "keyword",
                                        },
                                        "Region": {
                                            "type": "keyword",
                                        },
                                        "RegionName": {
                                            "type": "keyword",
                                        },
                                        "TimeZone": { # 시간대 정보
                                            "type": "keyword",
                                        },
                                        "City": { # 도시 정보
                                            "type": "keyword",
                                        },
                                        "Zip": { # 우편번호 정보
                                            "type": "keyword",
                                        },
                                        "Isp": { # ISP 정보
                                            "type": "keyword",
                                        },
                                        "Org": { # 조직 정보
                                            "type": "keyword",
                                        },
                                        "As": { # AS 정보
                                            "type": "text",
                                            "fields": { # .keyword 필드 추가
                                                "keyword": {
                                                    "type":         "keyword",
                                                    "ignore_above": 512, #필요에 따라 길이 제한 설정
                                                },
                                            },
                                        },
                                        "location": { #위치 정보
                                            "type": "geo_point",
                                                #{
                                                #    "lat": 33.44,
                                                #    "lon": -112.22 이런 형식
                                                #}
                                        },
                                    },
                                },
                            }
                        }
                    },
                },
            }
        },
        "aliases": {
                        "categorical_index": {},
                },
        },
        "_meta": {
                "description": "categorical 유형의 컴포넌트, NDR 간 호환되는 로그 필드",
                "version":     1,
        },
}


## NDR index template

index_patterns = "siem-ndr-*"
index_name = "siem-ndr-networkbehavior-event"
template_name = "siem-ndr-networkbehavior-event-index-template"
template = {

    "index_patterns": index_patterns,

    "priority":       298,
    "composed_of": [
        Common_component_template_name,
        NDR_categorical_component_template_name
    ],
    "template": {
        "settings": {
            "number_of_shards":   1,
            "number_of_replicas": 0,
            "mapping": {
                      "total_fields": {
                        "limit": 2000  # 여기서 필드 개수 제한 설정 (동적 필드 설정 시 너무 많으면 오류 발생하는 점을 해소하기 위한 방법)
                      }
                    }
        },
        "mappings": {
            "properties": {
                "unique": {
                    "properties": {
                        "suricata": {
                            "properties": {
                                "eve_log":{
                                    "properties": {
                                        # 주요 전역적인 Suricata eve-log 필드
                                        "src_ip": {"type":"ip"},
                                        "src_port": {"type":"keyword"},
                                        "dest_ip": {"type":"ip"},
                                        "dest_port": {"type":"keyword"},
                                        "proto": {"type":"keyword"},
                                        "direction": {"type":"keyword"},
                                        "flow_id": {"type":"keyword"},
                                        "pkt_src": {"type":"keyword"},
                                        "event_type": {"type":"keyword"},
                                        # /* ... */
                                    }
                                },
                                "payload": {
                                    "properties": {
                                        "type": {"type":"keyword"}, # "file"(파일분석결과) or "command"(명령어관련(RCE))
                                    }
                                }
                            }
                        },
                        "mitmproxy": {
                            "properties": {}
                        }
                    }
                }
            }
        }
    }
}