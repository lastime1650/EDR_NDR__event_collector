import socket

VPN_SERVER = "127.0.0.1"
VPN_PORT = 5959

VPN_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

VPN_SOCKET.connect((VPN_SERVER, VPN_PORT))


MY_VIP = "172.31.1.2"

from scapy.all import *
import time
time.sleep(1)

ping_packet = IP(src=MY_VIP, dst="8.8.8.8") / \
                              ICMP(type=8, code=0)

VPN_SOCKET.sendall(raw(ping_packet))