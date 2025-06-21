import socket, os, subprocess, threading, json, copy, time

from typing import Optional

# lua 송신 데이터 구조체 정의

# 1. type: packet
# -> 실제 바이너리가 전송된다.
class packet_payload():
    def __init__(self, input_packet_dict:dict):
        import base64
        
        self.binary =  base64.b64decode(
            input_packet_dict["binary"]
        )
        
    def get_binary(self) -> bytes:
        return self.binary

# 2. type: file
# -> 바이너리가 저장된 절대경로가 전송된다.
class file_payload():
    def __init__(self, input_file_dict:dict):
        self.binary_path:str = input_file_dict["path"]
        self.binary = b''
        
    def get_binary(self) -> bytes:
        if len(self.binary) < 1:
            with open(self.binary_path, "rb") as f:
                self.binary = f.read()
                
        return self.binary

class parsing_payload():
    def __init__(self, payload_metadata:dict):
        self.binary = b''
        if "packet" in payload_metadata:
            parsed = packet_payload(payload_metadata["packet"])
            self.binary = parsed.get_binary()
            
        elif "file" in payload_metadata:
            parsed = file_payload(payload_metadata["file"])
            self.binary = parsed.get_binary()
            
        else:
            # print("처리 할수 없는 payload 처리 by lua ")
            self.binary = None
    
    def get_binary(self) -> Optional[bytes]:
        return self.binary
        


from Logging.logger import Logger
class payload_log_process():
    def __init__(self, sock_path:str, logger:Logger):
        
        # 로거
        self.logger = logger
        
        # 이전 Sock 파일이 있는 경우 제거
        if os.path.exists(sock_path):
            os.remove(sock_path)
            
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        print(f"Listening on socket {sock_path}")
        self.s.bind(sock_path)
        self.s.listen(10) # maximum lua script count
        pass
    
    def Receive(self):
        

        
        while True:
            conn, addr = self.s.accept() # payload-log는 등록한 lua 스크립트 마다 연결됨
            
            # 독립 소켓 처리 스레드 생성/실행 
            threading.Thread(
                target=self.connected_by_lua,
                args=(
                    conn,
                ),
                daemon=True
            ).start()
    
    def connected_by_lua(self, conn:socket):
        self.payload_metadatas:list[dict] = []
        needed_data = ""
        needed_continous_count = 0
        
        while True:
            # lua 스크립트로부터 페이로드를 제공받으나, 추가적인 파싱을 해야함
            
            # Dict 타입으로 변환이 가능해야한다.( list[dict]일 수 있다 (Suricata의 멀티스레딩에 의하여) )
            data = conn.recv(9999999).decode()
            if not data:
                break
            
            if len(needed_data) > 0:
                data = needed_data + data
                needed_data = ""
            
            for payload_metadata in data.split("\n"):
                json_data:dict = {}
                if len(payload_metadata) > 0:
                    try:
                        json_data = json.loads(payload_metadata)
                    except:
                        needed_data = payload_metadata
                        needed_continous_count += 1
                        break
                
                
                
                    self.Processing_event(json_data) # JSON 전송
                continue
                    
            if len(needed_data) == 0:
                needed_continous_count = 0
                
            continue
   
        print("수리카타 sock NONE받음")
        
        self.Shutdown()
        quit()
    
    # 동기
    def Processing_event(self, payload_metadata:dict):
        binary:Optional[bytes] = parsing_payload(
                payload_metadata=payload_metadata
            ).get_binary()
        if not binary:
            print("suricata-lua-bytes없음")
            return
        #print(binary)
        return
    
    
    # Sock 연결 실패시
    def Shutdown(self):
        
        # suricata 강제종료
        subprocess.run(
            ["pkill", "-f", "suricata"],
            check=False
        )
