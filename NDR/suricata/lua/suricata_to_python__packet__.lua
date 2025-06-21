local Posix_ = require("posix") -- posix
local Posix__socket = Posix_.sys.socket

local SOCKET_PATH = "/var/run/suricata/payload.sock"
local Client_ID = "lua_packet_sock"

local socket_client = nil

-- Python unix-stream 객체 파일에 연결후 client 객체 반환 
function Connect_to_Python__with_unix_stream()

    socket_client = Posix__socket.socket(Posix__socket.AF_UNIX, Posix__socket.SOCK_STREAM, 0) -- unix-stream 방식
    if not socket_client then
        print(string.format("Python 리시버와 UNIX STREAM 객체 생성 실패 \n"))
        return nil
    end

    local result = Posix__socket.connect(
                                            socket_client,
                                            {
                                                family = Posix__socket.AF_UNIX, 
                                                path = SOCKET_PATH,
                                            }
                                        )
    if result ~= 0 then
        print(string.format("Python 리시버와 UNIX STREAM 연결 실패 경로: %s \n", SOCKET_PATH))
        socket_client = nil
        return nil
    end

    print(string.format("socket_client 연결 성공 \n") )
    return socket_client
end

-- Python Unix-Stream에 Send
function Send_to_Python(json_data)

    if not socket_client then
        return -1
    end

    Posix__socket.send(
        socket_client,
        json_data
    )

    return 0
    
end

-- bytes -> base64 변환
local base64_ = require("base64")
function Bytes_to_base64(bytes)
    return base64_.encode(bytes)
end

-- JSON 생성
local json_ = require("cjson")
function Make_Json(base64, ISO_timestamp, source_ip, source_port, destination_ip, destination_port )
    
    return json_.encode(
        {
            packet = {
                binary = base64,
                timestamp = ISO_timestamp,
                source_ip = source_ip,
                source_port = source_port,
                destination_ip = destination_ip,
                destination_port = destination_port,
            }
        }
    )
end

-- 현재 시간 (ISO 형식)가져오기
local socket_for_timestamp = require("socket")
function Get_Current_Timestamp()

    local now = socket_for_timestamp.gettime()  -- float: 초 + 소수점
    local sec = math.floor(now)
    local ms = math.floor((now - sec) * 1000)

    local t = os.date("!*t", sec)  -- UTC 기준 (Z)
    return string.format(
        "%04d-%02d-%02dT%02d:%02d:%02d.%03dZ",
        t.year, t.month, t.day,
        t.hour, t.min, t.sec,
        ms
    )
    
end

-- 초기 
function init(args) 
    local needs = {}

    -- 필요한 정보 요구를 needs 에 등록

    needs["type"] = "packet"
    
    return needs 
end

-- SetUp
function setup(args)

    print("type - packet lua 등록됨")
    socket_client = Connect_to_Python__with_unix_stream()
    if not socket_client then
        print("lua - unix_stream - 등록실패")
        return -1 -- 등록 실패 ( 원인: 소켓 객체 연결 및 생성 실패)
    end

    return 0
end


function log(args)
    -- 타임스탬프 seconds & microseconds // 1970-01-01 00:00:00 UTC.
    local sec, usec = SCPacketTimestamp()



    local ipver, srcip, dstip, proto, sp, dp = SCPacketTuple()


    -- 패킷에서 페이로드 가져와야함

    -- payload = SCPacketPayload() -- reference: https://docs.suricata.io/en/suricata-7.0.10/lua/lua-functions.html
    local payload
    -- print("log - payload 호출됨")
    payload = SCPacketPayload() -- 패킷 바이너리 데이터
    -- print(payload)
    -- print(string.format("->%s",string.sub(payload,1,2)))
    
    -- 패킷 바이너리를 Base64로 인코딩
    local base64__binary = Bytes_to_base64(payload)
    -- 길이 검증
    if #base64__binary < 1 then
        return 0
    end
    -- srprint(payload)
    -- 현재 시간 구하기
    ISO_timestamp =  Get_Current_Timestamp()


    -- Python에게 전달
    local payload_log_json = Make_Json(
                base64__binary,
                ISO_timestamp,
                srcip,
                sp,
                dstip,
                dp
            )
    local json_ = string.format("%s\n", payload_log_json) -- \n 으로 전달해야 2개이상의 dict을 처리할 수 있도록 Python에서 쉽게 ('\n') 파싱이 가능함.
    
    

    -- 전송
    Send_to_Python(
        json_
    )
    
    

    return 0
end

-- 해제
function deinit (args)
    if socket_client then
        Posix__socket.shutdown(socket_client, Posix__socket.SHUT_RDWR) -- 소켓 객체 닫기 likes close()
        os.exit(Posix__socket) -- 소켓 제거
        socket_client = nil
    end
    return 0
end