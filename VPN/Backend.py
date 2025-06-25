


from Tunnel_Interface_Manager import Tunnel_Manager

import socket

from typing import Optional

class VPN_Backend():
    def __init__(
        self,
        VIP_POOL_SUBNET:str ="172.31.1.0/24"
    ):
        
        
        # VPN의 Core 핵심 매니저
        # Tunnel 인터페이스 + VIP 할당 관리
        self.Tunnel_Manager = Tunnel_Manager(VIP_POOL_SUBNET) #- Backend에서 관리 
        
        

    def Processing_by_Client(
        self,
        client_ip:str,
        client_socket:socket.socket,
    ):
        My_VIP:Optional[str] = None
        
        # VIP 할당 요청
        My_VIP =  self.Tunnel_Manager.VIP_manager.Allocate_VIP(
            client_ip=client_ip,
            client_socket=client_socket,
        )
        
        '''from Client_Manager import VPN_Client_Manager,DataSignal,DataStruct
        
        Client = VPN_Client_Manager(
            client_socket=client_socket,
            client_ip=client_ip,
        )
        
        # 연결성공 전송
        Client.Send(
            signal=DataSignal.VIP_SUCCESS,
            VIP=My_VIP,
            data=b"Welcome - VPN!@#"
        )'''
        import json
        # VIP IP 전달
        client_socket.sendall(
            str(json.dumps(
                {
                    "vip": My_VIP,
                    "subnetmask": self.Tunnel_Manager.VIP_manager.VIP_Subnet,
                    "gw": self.Tunnel_Manager.VIP_manager.VIP_GW,
                }
            )).encode()
        )
        
        
        while True:
            # TEST
            packet_By_client = client_socket.recv(1500)
            
            if len(packet_By_client) == 0:
                # 연결 강제 끊김 ( RST )
                # .. VIP Pool 해제
                
                client_socket = None
                return
            
            # 터미널 인터페이스에 패킷 전달
            self.Tunnel_Manager.SendTunnelQueue.put(
                packet_By_client
            )
            