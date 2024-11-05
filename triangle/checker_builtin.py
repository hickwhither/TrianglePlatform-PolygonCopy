

def token_checker(output:str, answer:str):
    output = output.strip().split()
    answer = answer.strip().split()
    if len(output) < len(answer):
        return 1, "EOF unexpected"
    for i in range(len(answer)):
        if output[i] != answer[i]:
            return 1, f"Token #{i}. Expected {answer[i]} found {output[i]}"
    return 0, "Accepted"

def line_by_line_checker(output:str, answer:str):
    output = output.strip().split('\n')
    answer = answer.strip().split('\n')
    if len(output) < len(answer):
        return 1, "EOF unexpected"
    for i in range(len(answer)):
        if output[i].strip() != answer[i].strip():
            return 1, f"Line #{i+1}. Expected {answer[i]} found {output[i]}"
    return 0, "Accepted"

def get_float_compare_checker(eps:float=1e-6):
    def float_compare_checker(output:str, answer:str):
        output = output.strip().split()
        answer = answer.strip().split()
        if len(output) < len(answer):
            return 1, "EOF unexpected"
        for i in range(len(answer)):
            try:
                out_val = float(output[i])
                ans_val = float(answer[i])
                if abs(out_val - ans_val) > eps and abs(out_val - ans_val) > eps * max(abs(out_val), abs(ans_val)):
                    return 1, f"Token #{i}. Expected {ans_val} found {out_val}, difference exceeds {eps}"
            except ValueError:
                if output[i] != answer[i]:
                    return 1, f"Token #{i}. Expected {answer[i]} found {output[i]}"
        return 0, "Accepted"
    return float_compare_checker