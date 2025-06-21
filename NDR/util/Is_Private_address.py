import ipaddress


def is_Private(
    ip_address:str,
)->bool:
    return ipaddress.ip_address(
        ip_address
    ).is_private
    
    
"""print(
    is_Private(
        "10.0.0.1"
    )
)"""