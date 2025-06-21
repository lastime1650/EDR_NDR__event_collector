

# 수리카타
from suricata.suricata import SuricataManager

# --- mitmproxy 애드온 로직 ---
class Suricata:
    def __init__(
        self,
        KAFKA_IP:str="kafka",
        KAFKA_PORT:int=29092,
        ElasticSearch_IP:str="elasticsearch",
        ElasticSearch_PORT:int=9200,
        
        ):
        
        
        # 엘라스틱서치 + Kafka 올인원 객체
        from Logging.logger import Logger
        self.Logger = Logger(
            KAFKA_IP=KAFKA_IP,
            KAFKA_PORT=KAFKA_PORT,
            ElasticSearch_IP=ElasticSearch_IP,
            ElasticSearch_PORT=ElasticSearch_PORT,
        )
        
        # 수리카타 로그 수신 객체 (eve-log + by lua script)
        self.SuricataManager = SuricataManager(
            logger=self.Logger
        )
        
        
        # SSL/TLS Inspection을 위한 PolarProxy 객체
        from suricata.polarproxy import PolarProxy
        self.PolarProxy = PolarProxy()
        
        
    def start(self):
        print("-----시작-----\n")
        #1. 폴라 프록시 실행
        self.PolarProxy.Start_Proxy()
        
        #2. 수리카타 실행
        self.SuricataManager.start_() # Blocking
        
        
        import time, subprocess
        time.sleep(3)
        subprocess.Popen("suricata -c /etc/suricata/suricata.yaml -q 0", shell=True)
        
    
Suricata(
    KAFKA_IP="0.0.0.0",
    ElasticSearch_IP="172.30.1.254"
).start()










import threading, signal

exit_event = threading.Event()

def signal_handle(signumber, frame):
    exit_event.set()

signal.signal(
    signal.SIGTERM,
    signal_handle
)

exit_event.wait() # 종료대기