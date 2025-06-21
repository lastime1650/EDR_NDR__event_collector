import socket, os, subprocess, threading, json

from Logging.logger import Logger
class eve_log_process():
    def __init__(self, sock_path:str, logger:Logger):
        
        # 로거
        self.logger = logger
        
        
        # 맥주소 테이블
        from util.Get_MacAddress import Get_MacAddress
        self.MAC_Table = Get_MacAddress()
        
        
        
        # 이전 Sock 파일이 있는 경우 제거
        if os.path.exists(sock_path):
            os.remove(sock_path)
            
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        print(f"Listening on socket {sock_path}")
        self.s.bind(sock_path)
        self.s.listen(1)
        pass
    
    def Receive(self):
        

        conn, addr = self.s.accept() # eve-log는 딱 하나와 연결됨
        while True:
            # 수신된 데이터는 무조건 Dict 형태(기본본) 또는 List[Dict]일 수 있음
            data = conn.recv(4096).decode()
            if not data:
                break
            
            data_list:list[str] = data.split("\n")
            
            
            # 비동기 이벤트 처리 -> self.Receive 스레드는 빠르게 회전되어야 한다. ( 수리카타의 탐지 이벤트가 실시간 발생하므로 )
            threading.Thread(
                target=self.Processing_event,
                args=(
                    data_list,
                ),
                daemon=True
            ).start()
            
        
            
        print("수리카타 sock NONE받음")
        
        self.Shutdown()
        quit()
    
    
    # 비동기 처리
    def Processing_event(self, data_list:list[dict]):
        '''
        
            - "data_list" 인자 : eve-log 데이터 1개 이상
            
            - LOGIC
            1) eve-log dict 수신
            2) kafka 전달
            
        '''
        for data in data_list:
            
            if len(data) == 0:
                continue
            
            event_json = {}
            
            if "mokpo" in data.lower():
                print("[MOKPO]", flush=True)
            
            try:
                event_json = json.loads(data)
            except:
                continue
            
            ISO_timestamp  = self.convert_ISO_timestamp( event_json["timestamp"] )
            # ElasticSearch ISO 형식으로 변환필요
            
            
            # 로깅
            threading.Thread(
                target=self.send_log,
                args=(ISO_timestamp, event_json),
            ).start()
            '''self.send_log(
                iso_timestamp=ISO_timestamp,
                eve_log=event_json,
            )'''
            
    
    def send_log(
        self,
        iso_timestamp:str,
        eve_log:dict,
    ):
        # 패킷 흐름
        bound_type = "" # Inbound , Outbound, same ( 같은 내부망 끼리 )
        
        # 외부망 및 내부망 구별 필요
        from util.Is_Private_address import is_Private
        Internal_Ip = ""
        External_Ip = ""
        if is_Private(
            eve_log["src_ip"] # 소스아이피를 넘겨서 이것이 "내부망"에 해당하는 대역인가? 
        ):
            Internal_Ip = eve_log["src_ip"] # 내부망
            External_Ip = eve_log["dest_ip"]
            if is_Private(
                eve_log["dest_ip"]
            ):
                bound_type = "same"
                # 출발 및 목적 IP가 "내부망"으로 같은 경우,
                pass
            else:
                bound_type = "outbound"
        else:
            External_Ip = eve_log["src_ip"] # 외부망 ( 출발 및 목적 IP가 같은 내부망일 수 있음 )
            Internal_Ip = eve_log["dest_ip"]
            bound_type = "inbound"
            
        
        # 사내망 호스트의 MAC주소 추출
        Internal_Ip_Mac_Address = self.MAC_Table.Get_MacAddress_by_ip( Internal_Ip )
        
        
        from util.Get_GeoIP import GeoIP
        
        self.logger.Send_Log(
                data={
                    
                    # 공통 필드
                    "common": {
                        "Timestamp":iso_timestamp,
                        "Local_Ip": Internal_Ip,
                        "Mac_Address": Internal_Ip_Mac_Address,
                    },
                    
                    # NDR 전용 필드
                    "categorical": {
                        "bound_type": bound_type,
                        "protocol": eve_log["proto"],
                        "external_ip_info": {
                            # "ip": External_Ip,
                            "geoip": {},#GeoIP(External_Ip).Output()
                        },
                        
                    },
                    
                    # unique.suricata 전용 필드
                    "unique":{
                        "suricata": {
                            "eve_log": eve_log,
                        }
                    }
                }
            )
            
    
    def convert_ISO_timestamp(self, eve_log_timestamp)->str:
        # eve_log_timestamp -> 2025-06-03T14:58:58.937528+0900
        return eve_log_timestamp[:-8]
        
    
    # Sock 연결 실패시
    def Shutdown(self):
        
        # suricata 강제종료
        subprocess.run(
            ["pkill", "-f", "suricata"],
            check=False
        )