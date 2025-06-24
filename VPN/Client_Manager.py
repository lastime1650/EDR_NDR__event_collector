import socket
from typing import Optional
import base64

from enum import Enum 
class DataSignal(Enum):
    VIP_SUCCESS = 1,
    VIP_UNSUCCESS = 2,
    
    CONNECT_SUCCESS = 3,
    CONNECT_UNSUCCESS = 4,
    
    DATA = 5,
    
    DISCONNECT = 6,
    
# 서로 전달하는 데이터 체계 ( JSON )

import json 
class DataStruct():
    def __init__(
        self,
        data_signal: DataSignal,
        VIP:Optional[str],
        data:bytes,
    ):
        self.data_signal = data_signal
        self.VIP = VIP
        
        self.data = data
        
        self.JSON_DATA ={
            
            "head": {
                "data_signal": data_signal.name,
                "VIP": VIP, # 클라이언트 VIP (VIP 할당 실패인 경우 null(None) )
            },
            "body": data # scapy 패킷 데이터 
            
        }
        
    def Output_JSON(self)->str:
        return json.dumps(self.JSON_DATA, ensure_ascii=False )
        


class VPN_Client_Manager():
    def __init__(
        self, 
        client_socket:socket.socket,
        client_ip:str,
    ):
        self.client_socket = client_socket
        
        self.client_ip = client_ip
        
        self.my_VIP: str = ""
        
    
    def Receive(self)->DataStruct:
        
        recv:bytes = self.client_socket.recv(99999)
        
        recv_json = json.loads(recv)
        
        
        return DataStruct(
            data_signal= DataSignal[recv_json["head"]["data_signal"]],
            VIP=recv_json["head"]["VIP"],
            data= base64.b64decode(recv_json["body"]["data"])
        )
    
    def Send(self,signal:DataSignal,VIP:str,data:bytes):
        
        
        self.client_socket.sendall(
            DataStruct(
                data_signal= signal,
                VIP=VIP,
                data= base64.b64encode(data)
            ).Output_JSON().encode()
        )
    
    