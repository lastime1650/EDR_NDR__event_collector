

local cjson = require "cjson"

-- 초기 
function init(args) 
    local needs = {}

    -- 필요한 정보 요구를 needs 에 등록

    needs["type"] = "streaming"
    needs["filter"] = "tcp" -- tcp/http
    
    return needs 
end

-- SetUp
function setup(args)
    print("type - packet lua 등록됨")
    return 0
end


function log(args)

    data = SCStreamingBuffer()
    hex_dump(data)

    return 0
end

function match(args)
    print("match 호출됨")
    return 0
end

-- 해제
function deinit (args)
    return 0
end