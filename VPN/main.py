# 자체 개발 VPN
# - 서버는 Tun 터미널 인터페이스를 기반으로 VIP Pool 서브넷을 구성하여 구현한다. 

from Tunnel_Interface_Manager import Tunnel_Manager

import socket
from typing import Optional

from enum import Enum

import threading

class Server_Proto_Mode(Enum):
    # name / port_num
    TCP_mode = 5959 # TCP 서버형
    UDP_mode = 6060 # UDP 서버형

class VPN_Server():
    def __init__(
        self,
        ServerMode:Server_Proto_Mode,
        ServerIp:str,
    ):
        # 서버 소켓 생성
        self.VPN_Server_Socket:Optional[socket.socket]
        if ServerMode == Server_Proto_Mode.TCP_mode:
            self.VPN_Server_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
        elif ServerMode == Server_Proto_Mode.UDP_mode:
            self.VPN_Server_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

        self.VPN_Server_Socket.bind((ServerIp, int(ServerMode.value)))
        
        self.VPN_Server_Socket.listen(999)
        
        # VPN 통합 백엔드 매니저
        from Backend import VPN_Backend
        self.VPN_Backend = VPN_Backend()
        
        
        
    def Start_Server(self):
        if not self.VPN_Server_Socket:
            raise "self.VPN_Server_Socket 소켓 객체가 None임"
        
        
        
        while True:
            client_socket, info = self.VPN_Server_Socket.accept()
            threading.Thread(
                target=self.VPN_Backend.Processing_by_Client,
                args = (
                    str(info[0]), # Client IP
                    client_socket # Client 소켓
                )
            ).start()
            
    

VPN_Server(
    Server_Proto_Mode.TCP_mode,
    "127.0.0.1",
).Start_Server() # VPN 서버 실행