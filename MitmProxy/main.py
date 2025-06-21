from mitmproxy import http, ctx


# --- mitmproxy 애드온 로직 ---
class MITMPROXY_:
    def __init__(self):
        pass

    def load(self, loader):
        print(" MITM PROXY 로드됨 ")
        pass
        
        
        
    def done(self):
        pass
        
    # SIGTERM 처리
    def signal_handler(self, signal, frame):
        print("SIGNAL TERMINATED")
        self.done()

    # --- 표준 mitmproxy 이벤트 핸들러들 ---
    def request(self, flow: http.HTTPFlow) -> None:
        # mitmproxy를 통과하는 HTTP/S 요청 처리
        client_ip = flow.client_conn.address[0]
        # ctx.log.info(f"[MITMPROXY HANDLER] Request from {client_ip} to {flow.request.pretty_url}")
        # Scapy 스레드와 정보를 공유하려면 Queue나 다른 IPC 메커니즘 사용 고려
        print(f"[MITMPROXY HANDLER] Request from {client_ip} to {flow.request.pretty_url}")


    def response(self, flow: http.HTTPFlow) -> None:
        # mitmproxy를 통과하는 HTTP/S 응답 처리
        # ctx.log.info(f"[MITMPROXY HANDLER] Response for {flow.request.pretty_url}")
        print(f"[MITMPROXY HANDLER] Response for {flow.request.pretty_url}")

# mitmproxy가 로드할 애드온 인스턴스
addons = [
    MITMPROXY_()
]