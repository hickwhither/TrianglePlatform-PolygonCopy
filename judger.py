import subprocess, os, shutil
import json
import sys

IGNORE_LINUX_FLAG = False
MEMORY_LIMIT_SYSTEM = 256
TIME_LIMIT_SYSTEM = 6

JUDGE_FOLDERPATH = "workspace"
USER_FOLDERPATH = "user_submissions"


class InternalJudging(Exception): # Fault by problem setter
    def __init__(self, code, content, err):
        self.code = code
        self.content = content
        self.err = err
    def __repr__(self):
        return self.code + '\n' + self.content + '\n' + self.err

class InternalError(Exception):
    def __init__(self, path, *err):
        self.path = path
        self.err = err
    def __repr__(self):
        return f"File {self.path}:\n" + "\n".join(self.err)


_memory_warning_shown = False
def create_process(cmd, memory_limit, cwd):
    global _memory_warning_shown
    if sys.platform.startswith('linux') or IGNORE_LINUX_FLAG:
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
            preexec_fn=lambda: __import__('resource').setrlimit(
            __import__('resource').RLIMIT_AS,
            (memory_limit * 1024 * 1024, memory_limit * 1024 * 1024)),
            cwd = cwd)
    else:
        if not _memory_warning_shown:
            print("\033[93mWARNING: THIS SYSTEM IS NOT LINUX, MEMORY LIMIT WONT WORKING.\033[0m")
            print("\033[92mSet `IGNORE_LINUX_FLAG = True` in this file if you wanna use it anyways\033[0m")
            _memory_warning_shown = True
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd)
    return process


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
def float_compare_checker(output:str, answer:str, eps:float=1e-6):
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


class Triangle:
    """
    Dont be cruel for all of this. Im tryna faking Polygon
    You can try something else im developing
    """

    languages: dict[str, dict]
    """
    {
        "id": "python3",
        "file_extension": ".py",
        "compilation": null,
        "execution": "python {name}.py",
        "version": "python -V"
    }   
    """
    def __init__(self, languages_folder:str = 'languages'):
        self.languages = {}
        for i in os.listdir('languages'):
            if i.endswith('.json'):
                language_name = i[:-5]
                with open(os.path.join('languages', i), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if sys.platform.startswith('win32'):
                    data['compilation'] = data['compilation'].replace('.out', '.exe') if data['compilation'] else None
                    data['execution'] = data['execution'].replace('.out', '.exe')
                
                p = subprocess.Popen(data['version'], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
                stdout, stderr = p.communicate()
                data['version'] = stdout.decode().strip()

                if p.returncode==0:
                    self.languages[language_name] = data
                    print(f"✅ Checked {language_name}", data['version'])
                else:
                    print(f"❌ Failed {language_name}:")
                    print(stdout.decode())
                    print(stderr.decode())


    config: dict[str,int|dict|list]
    compile_result:dict

    def compile_single(self, i):
        cf = self.config[i]
        source_file = cf['path']
        language = self.languages.get(cf['language'])

        if not language:
            raise InternalError(source_file, f"Language not found")
        if not os.path.exists(os.path.join(JUDGE_FOLDERPATH, source_file)): # File not found
            raise InternalError(source_file, f"File not found")
        if not source_file.endswith(language['file_extension']): # Extension part not correct
            raise InternalError(source_file, f"Extension part mot matching with the language")
        
        source_name = source_file[:-(len(language['file_extension']))]
        
        if language['compilation']: # If have compile
            cmd = language['compilation'].format(name=source_name)
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=JUDGE_FOLDERPATH)
            stdout, stderr = process.communicate()
            if process.returncode != 0: # Compile error
                raise InternalError(source_file,
                                    f"Returned code {process.returncode}",
                                    stdout.decode() + '\n' + stderr.decode())
            self.compile_result[i] = "Compiled successfully"
        else: self.compile_result[i] = "No need to compile"
        self.config[i]['source_name'] = source_name
        self.config[i]['language'] = language

    def compile(self):
        """
        Compile everything in workspaces.
        InternalError if file/language not found or compile error
        """
        # Workspace config
        with open(os.path.join(JUDGE_FOLDERPATH, "config.json"), "r", encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.compile_result = {}
        
        for i in ['generator', 'solution']:
            self.compile_single(i)
        if isinstance(self.config['checker'], dict): self.compile_single('checker')
        if isinstance(self.config['validator'], dict): self.compile_single('checker')
            
    
    def process_byid(self, id, memorylimit=MEMORY_LIMIT_SYSTEM, *args):
        source_name = self.config[id]['source_name']
        cmd = self.config[id]['language']['execution'].format(name=source_name).split() + list(args)
        return create_process(cmd, memorylimit, JUDGE_FOLDERPATH)

    def single_test(self, input: bytes, user_process: 'SourceCode') -> tuple[str, str, int, str]:
        """
        Return tuple of output, answer, verdictcode, checker_response
        """
        if isinstance(self.config['validator'], dict):
            validator = self.process_byid('validator')
            stdout, stderr = validator.communicate(input, timeout=TIME_LIMIT_SYSTEM)
            if validator.returncode:
                raise InternalJudging(validator.returncode, "Validator didn't return 0", stdout.decode() + '\n' + stderr.decode())

        userout, usererr, usercode = user_process.run(input, memory_limit=self.config['memorylimit'], time_limit=self.config['timelimit'])
        if usercode:
            return "", "", usercode, ""
        
        try:
            solution = self.process_byid('solution', self.config['memorylimit'])
            solutionout, solutionerr = solution.communicate(input, timeout=self.config['timelimit'])
            if solution.returncode:
                raise InternalJudging(solution.returncode, "Solution didn't return 0", stderr.decode())
        except subprocess.TimeoutExpired:
            solution.kill()
            raise InternalJudging(124, "Solution time limit", stderr.decode())
        except MemoryError:
            solution.kill()
            raise InternalJudging(124, "Solution out of memory", stderr.decode())


        if not isinstance(self.config['checker'], dict):
            if self.config['checker'] == 'token': checker = token_checker
            if self.config['checker'] == 'line': checker = line_by_line_checker
            if self.config['checker'] == 'float':
                checker = lambda inp, out, eps=10**(-int(self.config['checker'][5:])): float_compare_checker(inp, out, eps)
            userout = userout.decode()
            solutionout = solutionout.decode()
            checker_returncode, checker_out = checker(userout, solutionout)
            return userout, solutionout, checker_returncode, checker_out
        else:
            with open(os.path.join(JUDGE_FOLDERPATH, 'input.txt'), 'wb') as f:
                f.write(input)
            with open(os.path.join(JUDGE_FOLDERPATH, 'output.txt'), 'wb') as f:
                f.write(userout)
            with open(os.path.join(JUDGE_FOLDERPATH, 'answer.txt'), 'wb') as f:
                f.write(solutionout)
            checker = self.process_byid('checker', MEMORY_LIMIT_SYSTEM, 'input.txt', 'output.txt', 'answer.txt')
            checkerout, checkererr = checker.communicate(timeout=TIME_LIMIT_SYSTEM)
            print(checker.args)
            if checker.returncode not in [0, 1, 2]:
                raise Exception(f"Checker returned code {checker.returncode}\n" + checkerout.decode() + '\n' + checkererr.decode())
            return userout.decode(), solutionout.decode(), checker.returncode, checkerout.decode()

    def run(self, user_process: 'SourceCode', limit_character:int = 2690):
        """
        Make sure that rejudged the code
        Run the whole code and assign self.result = a list of
        {
            "verdict": int,
            "response": reponse from judger,
            "input": ,
            "output":,
            "answer":
        }
        """
        self.results = []
        for args in self.config['tests']:
            gen = self.process_byid('generator', args, '> input.txt')
            stdout, stderr = gen.communicate(timeout=TIME_LIMIT_SYSTEM)
            if gen.returncode:
                res = {
                    "verdict": 69,
                    "response": f"Generator returned code {gen.returncode}\n" + stdout.decode() + '\n' + stderr.decode()
                }
                continue
            input = stdout.decode()
            try: output, answer, verdictcode, response = self.single_test(stdout, user_process)
            except InternalJudging as e:
                res = {
                    "verdict": 69,
                    "response": str(e)
                }
            else:
                input = input.replace('\r', '')
                output = output.replace('\r', '')
                answer = answer.replace('\r', '')
                res = {
                    "verdict": verdictcode,
                    "response": response,
                    "input": input[:limit_character] + "..." if len(input) > limit_character else input,
                    "output": output[:limit_character] + "..." if len(output) > limit_character else output,
                    "answer": answer[:limit_character] + "..." if len(answer) > limit_character else answer
                }
            self.results.append(res)
                

class SourceCode:
    source_code: str
    language: dict
    judger: Triangle
    def __init__(self, judger: Triangle): self.judger = judger
    
    def compile(self, code:str, language:str):
        self.language = self.judger.languages.get(language)
        if not self.language: raise InternalError("source", f"Language not found")

        for filename in os.listdir(USER_FOLDERPATH):
            file_path = os.path.join(USER_FOLDERPATH, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

        self.name = "source"
        with open(os.path.join(USER_FOLDERPATH, self.name+self.language['file_extension']), "wb") as f:
            f.write(code.encode())
        
        if self.language['compilation']:
            cmd = self.language['compilation'].format(name=self.name)
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=USER_FOLDERPATH)
            stdout, stderr = process.communicate()
            return stdout.decode(), stderr.decode(), process.returncode
        
        return "","",0

    def getprocess(self, memory_limit:int=256) -> subprocess.Popen:
        cmd = self.language['execution'].format(name=self.name)
        return create_process(cmd, memory_limit, USER_FOLDERPATH)

    def run(self, input:bytes=None, memory_limit:int=256, time_limit:float=1) -> tuple[bytes,bytes,int]: # stdout stderr code
        try:
            process = self.getprocess(memory_limit)
            stdout, stderr = process.communicate(input if input else None, timeout=time_limit)
        except subprocess.TimeoutExpired:
            process.kill()
            return process.stdout.read(), process.stderr.read(), 124
        except MemoryError:
            process.kill()
            return process.stdout.read(), process.stderr.read(), 137
        return stdout, stderr, process.returncode

