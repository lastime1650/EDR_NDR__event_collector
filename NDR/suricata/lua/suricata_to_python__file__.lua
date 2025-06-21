local Posix_ = require("posix") -- posix
local Posix__socket = Posix_.sys.socket

local SOCKET_PATH = "/var/run/suricata/payload.sock"

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

 -- 

-- 초기 
function init(args) 
    local needs = {}

    -- 필요한 정보 요구를 needs 에 등록

    needs['type'] = 'file'
    
    return needs 
end

-- SetUp
function setup(args)
    print("SetUp 호출됨")
    return 0
end


function log(args)

    -- 파일 인식되었을 때 감지
    -- /filestore 디렉터리내, sha256 앞 2자리 디렉터리에 보면 실제 바이너리가 파일로 저장되어 있음. 이를 활용가능

    print(" file - log 호출됨")
    local fileid, txid, name, size, magic, md5, sha1, sha256 = SCFileInfo()
    local state, stored = SCFileState()
    print(fileid, txid, name, size, magic, sha256)
    print(state, stored)

    return 0
end
-- 해제
function deinit (args)
    return 0
end