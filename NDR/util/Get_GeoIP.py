import requests
from typing import Optional


class GeoIP():
    
    def __init__(
        self,
        ip_Address:str
    ):
        query = f"http://ip-api.com/json/{ip_Address}"
        self.r:dict = requests.get(
            url=query
        ).json()
    
    def Output(self)->dict:
        
        if not (self.r["status"] == "success") :
            return {}
        
        
        return {
            "geoip": {
                "Ip": self.r["query"],
                "Country": self.r["country"],
                "Region": self.r["region"],
                "RegionName": self.r["regionName"],
                "TimeZone": self.r["timezone"],
                "City": self.r["city"],
                "Zip": self.r["zip"],
                "Isp": self.r["isp"],
                "Org": self.r["org"],
                "As": self.r["as"],
                "location": { #위치 정보
                    "lat": float(self.r["lat"]),
                    "lon": float(self.r["lon"]),
                },
            },
        }
        
print(        
    GeoIP("8.8.8.8").Output()
)