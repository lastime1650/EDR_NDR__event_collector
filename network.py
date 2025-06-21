import subprocess 


def command(cmd:str)->str:
    return subprocess.run(
        args=cmd.split(" "),
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    

def convert_ISO_timestamp(eve_log_timestamp)->str:
        
        print(eve_log_timestamp[:-8])
        return eve_log_timestamp[:-8]
    
convert_ISO_timestamp(
    '2025-06-03T14:58:58.937528+0900'
)