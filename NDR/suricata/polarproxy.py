import subprocess
import threading


class PolarProxy():
    def __init__(self, PolarProxy_program_PATH:str="/Polarproxy/PolarProxy"):
        self.PolarProxy_program_PATH = PolarProxy_program_PATH
        
    def Start_Proxy(self):
        threading.Thread(
            target=self.start_,
            daemon=True
        ).start()
        
        
    def start_(self):
        
        subprocess.run(
            f"{self.PolarProxy_program_PATH} -p 8443,80,443 -x /Cerification.cer --certhttp 8888 --pcapoverip 0.0.0.0:57012 > /dev/null 2>&1 &",
            check=False,
            shell=True
        )
        
        import time
        time.sleep(2)
        
        subprocess.run(
            f"nc 127.0.0.1 57012 | suricata -c /etc/suricata/suricata.yaml -r /dev/stdin",
            #check=False,
            shell=True
        )
        
        