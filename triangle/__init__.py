import os, subprocess, shutil, sys
import json
import time
from .runner import SourceCode
from . import checker_builtin


MEMORY_LIMIT_SYSTEM = 256
TIME_LIMIT_SYSTEM = 6

class Triangle:
    languages: dict
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
                    print(f"✅ Checked {language_name}")
                    print(data['version'])
                else:
                    print(f"❌ Failed {language_name}:")
                    print(stdout.decode())
                    print(stderr.decode())

    # Set memory and time limit
    memory_limit: float
    time_limit: float
    def set_limited(self, memory_limit, time_limit):
        self.memory_limit = memory_limit
        self.time_limit = time_limit

    # Compile and file compiled
    validator: SourceCode # Unused
    solver: SourceCode
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

    def run(self):
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
        def single_run(args):
            input, gen_error, gen_code, gen_duration, gen_memory = self.generator.run(args, MEMORY_LIMIT_SYSTEM, TIME_LIMIT_SYSTEM)
            if gen_code:
                return {
                    "verdict": 69,
                    "response": f"Generator returned code {gen_code}\n" + input + '\n' + gen_error
                }
            solver, solver_error, solver_code, solver_duration, solver_memory = self.solver.run(args=None, memory_limit=self.memory_limit, time_limit=self.time_limit, input=input)
            if solver_code:
                return {
                    "verdict": 3,
                    "response": f"Solver returned {gen_code}\n" + solver + '\n' + solver_error
                }
            user, user_error, user_code, user_duration, user_memory = self.user.run(args=None, memory_limit=self.memory_limit, time_limit=self.time_limit, input=input)
            if user_code:
                return {
                    "verdict": user_code,
                    "response": solver + '\n' + solver_error
                }
            if isinstance(self.checker, SourceCode):
                stdout, stderr, checker_code = self.checker.run("", MEMORY_LIMIT_SYSTEM, TIME_LIMIT_SYSTEM)
                checker_response = stdout + '\n' + stderr
            else:
                checker_code, checker_response = self.checker(user, solver)
            return {
                "verdict": checker_code,
                "response": checker_response,
                "input": input,
                "output": user,
                "answer": solver
            }
    
        self.results = []
        for args in self.tests:
            self.results.append(single_run(args))
