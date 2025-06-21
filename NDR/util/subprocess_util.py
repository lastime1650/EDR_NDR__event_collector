def input_subprocess_stdout_split(input:str)->list[str]:
    output: list[str] = []
    
    for row in input.split("\n"):
        
        is_blank = False
        tmp_string = ""
        for s in row:
            
            
            
            if is_blank == False and s == " ":
                is_blank = True
                if len(tmp_string) > 0:
                    output.append(
                        tmp_string
                    )
                    tmp_string = ""
                continue
            
            if is_blank and not (s == " "):
                is_blank = False
                tmp_string += s
                continue
            
            if is_blank:
                continue
            
            tmp_string += s
        
    return output