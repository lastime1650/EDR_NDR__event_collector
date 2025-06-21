import subprocess
import threading

class Get_MacAddress():
    def __init__(
        self,
        
    ):
        self.lock = threading.Lock()
        self.MacAddress_Table = {}
        '''
        {
            "1.1.1.1": "AA:BB:CC:DD:EE:FF"
        }
        '''
        
    def Get_MacAddress_by_ip(
        self,
        ip_Address:str
        )->str:
        
        self.result:str = subprocess.run(
            args = f"arp {ip_Address} | grep {ip_Address}",
            shell=True,
            text=True,
            capture_output=True
        ).stdout
        
        
        
        from util.subprocess_util import input_subprocess_stdout_split
        
        # ex) ['10.0.0.101', 'ether', '02:ac:30:2b:2c:35', 'C']
        arp_result = input_subprocess_stdout_split(self.result)
        
        MAC_ADDRESS = "incomplete"
        if ip_Address == arp_result[0]:
            try:
                MAC_ADDRESS = str(arp_result[2])
                self.input_table( # 테이블 저장
                    ip_Address,
                    MAC_ADDRESS
                )
            except:
                MAC_ADDRESS = self.get_mac_by_table( # 테이블 저장
                    ip_Address
                )
            finally:
                return MAC_ADDRESS
        
        return ""
        
    def input_table(
        self, 
        ip:str,
        mac:str
    ):
        with self.lock:
            self.MacAddress_Table[ip] = mac
            
        return

    def get_mac_by_table(
        self,
        ip:str
    )->str:
        with self.lock:
            try:
                return self.MacAddress_Table[ip]
            except:
                return "incomplete"
