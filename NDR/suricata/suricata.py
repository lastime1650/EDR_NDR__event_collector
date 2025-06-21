import subprocess
import threading 
import json


from Logging.logger import Logger

class SuricataManager():
    def __init__(self, logger:Logger):
        
        # 0. 로거
        self.logger = logger
        
        # eve-log 처리 객체
        from suricata.event_processing.eve_log import eve_log_process
        self.eve_log_process = eve_log_process(
            sock_path="/var/run/suricata/eve.sock",
            logger=self.logger
        )
        
        # payload-log 처리 객체
        from suricata.event_processing.lua_payload import payload_log_process
        self.payload_log_process = payload_log_process(
            sock_path="/var/run/suricata/payload.sock",
            logger=self.logger
        )
        
        ###########################
        
        
        
        
        pass
        
        
        
        
    def Start_Suricata(self):
        threading.Thread(
            target=self.start_,
            daemon=True
        ).start()
        
        
        
    def start_(self ):
        # suricata-IPS 실행
        
        # 2. lua payload 리스닝
        #threading.Thread(
        #    target=self.payload_log_process.Receive,
        #    daemon=True
        #).start()
        
        # 리스닝 실행
        
        # 1. eve 실시간 이벤트 리스닝 # eve.json을 unix-stream으로 라이브 수신
        threading.Thread(
            target=self.eve_log_process.Receive,
            daemon=True
        ).start()
        
        import time
        time.sleep(1)
        
        ### 수리카타 IPS 실행
        
        # suricata -c /etc/suricata/suricata.yaml -i {target_interface_name} -q 0 
        '''subprocess.run(
            ["suricata", "-c", "/etc/suricata/suricata.yaml", "-q", "0"], # 포그라운드
            check=False,
        )'''
    
    
        
    
    