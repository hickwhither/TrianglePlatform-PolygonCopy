import os, subprocess, shutil, sys
import json
import time
from .runner import SourceCode
from . import checker_builtin


MEMORY_LIMIT_SYSTEM = 256
TIME_LIMIT_SYSTEM = 6

class Triangle:
    force_stop: bool
    languages: dict
    results: dict
    def __init__(self, languages_folder:str = 'languages'):
        self.force_stop = False
        self.results = None
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
                    print(f"✅ Checked {language_name}")
                    print(data['version'])
                else:
                    print(f"❌ Failed {language_name}:")
                    print(stdout.decode())
                    print(stderr.decode())
    
    def setup(self):
        self.brute = None
        self.user = None
        self.generator = None
        self.results = None
        self.force_stop = False

    # Set memory and time limit
    memory_limit: float
    time_limit: float
    def set_limited(self, memory_limit, time_limit):
        self.memory_limit = memory_limit
        self.time_limit = time_limit

    # Compile and file compiled
    brute: SourceCode
    user: SourceCode
    generator: SourceCode
    checker: SourceCode

    def compile_any(self, id, source, language):
        language = self.languages.get(language)
        if not language: "TF is this language", "", 69420
        setattr(self, id, SourceCode(source, language))
        return getattr(self, id).compile()
    def use_builtin_checker(self, name:str):
        try:
            if name.startswith('token'): self.checker = checker_builtin.token_checker
            elif name.startswith('line'): self.checker = checker_builtin.line_by_line_checker
            elif name.startswith('float'): self.checker = checker_builtin.get_float_compare_checker(int(name[5:]))
            else: return "Checker type not found", 1
            return "Nice Chick(checker)", 0
        except ValueError as e:
            return f"Float eps error {e}", 1
    # Set generator args
    def set_tests(self, tests): self.tests = tests

    def run(self, limit_character:int = 2690):
        """
        Make sure that rejudged the code
        Run the whole code and assign self.result = a list of
        {
            "verdict": int,
            "response": reponse from checker/judger,
            "input":str,
            "output":str,
            "answer":
        }
        """
        def single_run(args) -> dict:
            input, gen_error, gen_code, gen_duration, gen_memory = self.generator.run(args, MEMORY_LIMIT_SYSTEM, TIME_LIMIT_SYSTEM)
            if gen_code:
                return {
                    "verdict": 69,
                    "response": f"Generator returned code {gen_code}\n" + input + '\n' + gen_error
                }
            brute, brute_error, brute_code, brute_duration, brute_memory = self.brute.run(args=None, memory_limit=self.memory_limit, time_limit=self.time_limit, input=input)
            if brute_code:
                return {
                    "verdict": 3,
                    "response": f"brute returned {gen_code}\n" + brute + '\n' + brute_error
                }
            user, user_error, user_code, user_duration, user_memory = self.user.run(args=None, memory_limit=self.memory_limit, time_limit=self.time_limit, input=input)
            if user_code:
                return {
                    "verdict": f"user code returned {user_code}",
                    "response": user + '\n' + user_error
                }
            if isinstance(self.checker, SourceCode):
                stdout, stderr, checker_code = self.checker.run("", MEMORY_LIMIT_SYSTEM, TIME_LIMIT_SYSTEM)
                checker_response = stdout + '\n' + stderr
            else:
                checker_code, checker_response = self.checker(user, brute)
            return {
                "verdict": checker_code,
                "response": checker_response,
                "input": input,
                "output": user,
                "answer": brute,
                "time": user_duration,
                "memory": user_memory
            }
        
        self.results = []
        for args in self.tests:
            if self.force_stop: break
            data:dict = single_run(args)
            if data.get("input") and len(data["input"]) > limit_character:
                data["input"] = data["input"][:limit_character] + "\n..."
            if data.get("output") and len(data["output"]) > limit_character:
                data["output"] = data["output"][:limit_character] + "\n..."
            if data.get("answer") and len(data["answer"]) > limit_character:
                data["answer"] = data["answer"][:limit_character] + "\n..."
            self.results.append(data)
            if self.force_stop: break

