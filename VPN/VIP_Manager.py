import ipaddress
import threading
import queue

import socket
from typing import Optional

class VIP_manager():
    def __init__(
        self,
        VIP_Subnet:str = "172.31.1.0/24"
    ):
        # Dict형 VIP 풀 관리
        self.VIP_Pool:dict = {
            #"1.1.1.1": { # VIP
            #    "client": {
            #                "ip": client_ip,
             #               "socket": client_socket,
            #            }
            #}
        }
        VIP_Subnet:str = VIP_Subnet
        
        # VIP Pool 내 메인 호스트 ( * 첫번째 호스트 )
        self.VIP_Pool__main_host:str  = list(ipaddress.ip_network(VIP_Subnet).hosts())[0]
        # VIP Pool 생성
        for host_ip in list(ipaddress.ip_network(VIP_Subnet).hosts())[1:]:
            self.VIP_Pool[str(host_ip)] = None # 초기화 
        
        self.mutex = threading.Lock()
    
    def Search_by_VIP(self, VIP:str)->Optional[dict]:
        # Reference Count 시스템 적용 추가 예정
        with self.mutex:
            try:
                if self.VIP_Pool[VIP]:
                    return self.VIP_Pool[VIP]
            except:
                return None
                
        return None
    
    def Allocate_VIP(self, client_ip:str, client_socket:socket.socket)->Optional[str]:
        with self.mutex:
            for VIP in self.VIP_Pool:
                VIP:str = VIP
                if self.VIP_Pool[VIP] == None:
                    self.VIP_Pool[VIP] = {
                        "client": {
                            "ip": client_ip,
                            "socket": client_socket,
                        }
                    }
                    return VIP
        
        return None
    
    def Free_VIP(self, client_ip:str, allocated_vip:str)->bool:
        with self.mutex:
            
            if self.VIP_Pool[allocated_vip]:
                if self.VIP_Pool[allocated_vip]["client"]["ip"] == client_ip:
                    self.VIP_Pool[allocated_vip] = None
                
        return False