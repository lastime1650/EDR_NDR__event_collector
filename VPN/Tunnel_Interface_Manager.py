#TUN 인터페이스 매니저
import os
import sys
import subprocess
from typing import Optional
import struct
import fcntl
import threading

import queue

from scapy.all import *
import scapy.layers
import scapy.layers
import scapy.layers
import scapy.layers.l2

class Tunnel_Manager():
    
    # --- 리눅스 상수 정의 ---
    TUNSETIFF = 0x400454ca
    IFF_TUN = 0x0001
    IFF_NO_PI = 0x1000
    
    def __init__(
        self, 
        VIP_Subnet:str = "172.31.1.0/24"
    ):
        
        from VIP_Manager import VIP_manager
        self.VIP_manager = VIP_manager(VIP_Subnet)
        
        
        self.VIP_Pool__Main_Host = self.VIP_manager.VIP_Pool__main_host # ex) 172.31.1.1
        
        self.tun_fd:int = -1  # tun 장치 파일 디스크립터
        self.mtu:int = 1500 # 패킷 당 사이즈
        
        self.SendTunnelQueue = queue.Queue()
        
        # 인터페이스 생성
        self.Create_interface()
        
        
        # 터널 Write 작업 무한 스레드
        threading.Thread(
            target=self.Loop_Write
        ).start()
        
        # 터널 Read 작업 무한 스레드
        threading.Thread(
            target=self.Loop_Read
        ).start()
    
    ##############################
    
    # 1. Tunnel - Write 
    def Loop_Write(self):
        while True:
            
            '''
            Recevied Packet Info
            
            - IP Layer
            -- Src: VIP
            -- Dst: Target ( 외부 호스트 )
            
            '밖으로 보내는 역할'
            
            '''
            
            # 클라이언트로부터 패킷 수신
            Packet_by_Client = self.SendTunnelQueue.get()
            
            IP_Checked_Full_Packet = None
            try:
                IP_Checked_Full_Packet = IP(Packet_by_Client)
            except:
                continue 
            
            VIP = IP_Checked_Full_Packet[IP].src
            
            # VIP Pool 할당받았는 지? 검증
            client_vip_info:Optional[dict] = self.VIP_manager.Search_by_VIP(
                VIP=VIP
            )
            if not client_vip_info:
                continue
            
            
            # Write -(Tun)-> 외부 호스트로 전송처리
            IP_Checked_Full_Packet.show()
            ready_packet:bytes = raw(IP_Checked_Full_Packet)
            self.Write(
                packet= ready_packet
            )
    
    
    # 2. Tunnel - Read
    def Loop_Read(self):
        while True:
            
            '''
            Recevied Packet Info
            
            - IP Layer
            -- Src: Target ( 외부 호스트 )
            -- Dst: VIP
            
            '안으로 들어와 Client 내부 전달함'
            
            '''
            
            # 터널 인터페이스로부터 패킷 수신
            Packet_by_External = self.Read()
            
            # IP 헤더 존재 검증 후 => Scapy 패킷 객체 획득
            IP_Checked_Full_Packet = None
            try:
                IP_Checked_Full_Packet = IP(Packet_by_External)
            except:
                continue 
            
            # VIP Pool 매니저에 "등록 되었는가?" 검증 
            VIP = str(IP_Checked_Full_Packet[IP].dst)
            
            client_vip_info:Optional[dict] = self.VIP_manager.Search_by_VIP(
                VIP=VIP
            )
            if not client_vip_info:
                continue
            
            # Client 전달 매체 (Queue) 추출
            IP_Checked_Full_Packet.show()
            client_socket:socket.socket= client_vip_info["client"]["socket"]
            client_socket.sendall(
                raw(IP_Checked_Full_Packet)
            )
    
    
    
    ##################################################################################
    
    def Create_interface(self):
        
        self.interface_name = "tun0"
        
        # 1. 인터페이스 생성
        self.tun_fd = os.open("/dev/net/tun", os.O_RDWR) # tun 장치 파일 디스크립터

        # 인터페이스 생성 요청
        ifr = struct.pack("16sH", self.interface_name.encode('utf-8'), self.IFF_TUN | self.IFF_NO_PI)
        fcntl.ioctl(self.tun_fd, self.TUNSETIFF, ifr)

        # IP 주소 할당 및 인터페이스 활성화
        self.subprocess_shell_(f"ip addr add {self.VIP_Pool__Main_Host}/24 dev {self.interface_name}")
        self.subprocess_shell_(f"ip link set dev {self.interface_name} up")
    
    def subprocess_shell_(self, cmd:str):

        subprocess.run(
            cmd,
            shell=True,
            check=True,
        )
    
    def Terminate_interface(self):
        
        os.close(
            self.tun_fd
        )
        
        # 인터페이스 제거 
        self.subprocess_shell_(
            f"ip link del {self.interface_name}"
        )
        
        
    ##################################################################################
    
    # 패킷을 외부로 내보냄
    def Write(self, packet:bytes)->int:
        if self.tun_fd < 1 :
            raise "Tun 인터페이스가 존재하지 않음"
        
        output = os.write(
            self.tun_fd,
            bytes(packet), # 전송할 패킷 전체
        )
        
        return output
        
    # 내보낸 패킷을 수신함
    def Read(self)->bytes:
        if self.tun_fd < 1 :
            return b'X'
        
        try:
            return os.read(
                self.tun_fd,
                self.mtu # 수신할 패킷 단위 사이즈 ( MTU )
            )
        except:
            self.Terminate_interface()
        
        