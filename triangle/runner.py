from uuid import uuid4
import os, shutil, sys
import subprocess
import psutil, time

IGNORE_LINUX_FLAG = False
_linuxflag_warning = False

class SourceCode:
    source_code: str
    language: dict
    compile_response: str
    """
    {
        "id": "cpp",
        "file_extension": ".cpp",
        "compilation": "g++ -Wall -O2 -lm -fmax-errors=5 -march=native -s {name}.cpp -o {name}.out",
        "execution": "{name}.out",
        "version": "g++ --version"
    }
    """
    file_extension: str
    compilation: str
    execution: str
    
    folder_name: str
    file_name: str
    def __init__(self, source_code:str, language:dict):
        self.file_extension = language['file_extension']
        self.compilation = language['compilation']
        self.execution = language['execution']

        self.folder_name = os.path.join("temp", str(uuid4()))
        self.file_name = os.path.join(self.folder_name, "source")
        os.mkdir(self.folder_name)
        with open(self.file_name + self.file_extension, "w", encoding="utf-8") as f:
            f.write(source_code)
    
    def compile(self) -> tuple:
        """
        Compile source and return tuple(stdout stderr code)
        """
        if self.compilation:
            cmd = self.compilation.format(name="source")
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.folder_name)
            stdout, stderr = process.communicate()
            return stdout, stderr, process.returncode
        return 0, ""
    
    def run(self, args:str=None, memory_limit:float=256, time_limit:float=1, input:str=None) -> tuple:
        """
        Run file and return stdout:str, stderr:str, process_returncode:int, duration:float(s), memory:float(MB)
        """
        global _linuxflag_warning
        cmd = self.execution.format(name="source")
        if args: cmd += ' ' + args
        try:
            if sys.platform.startswith('linux') or IGNORE_LINUX_FLAG:
                process = subprocess.Popen(
                    cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    preexec_fn=lambda: __import__('resource').setrlimit(
                        __import__('resource').RLIMIT_AS,
                        (memory_limit * 1024 * 1024, memory_limit * 1024 * 1024)),
                    shell=True, cwd=self.folder_name)
            else:
                if not _linuxflag_warning:
                    print("\033[93mWARNING: THIS SYSTEM IS NOT LINUX, `resource` library will not be used for limit memory.\033[0m")
                    print("\033[92mSet `IGNORE_LINUX_FLAG = True` in `triangle/runner.py` in this file if you wanna use it anyways\033[0m")
                    _linuxflag_warning = True
                if cmd.startswith('./'): cmd = cmd[2:]
                process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=self.folder_name)
            process_start_time = time.time()
            process_memory = psutil.Process(process.pid).memory_info().rss / (1024 * 1024)
            stdout, stderr = process.communicate(input.encode() if input else None, timeout=time_limit)
            process_duration = time.time() - process_start_time
            if process_memory > memory_limit:
                raise MemoryError
        except subprocess.TimeoutExpired:
            process.kill()
            return None, None, 124, 0, 0
        except MemoryError:
            process.kill()
            return None, None, 137, 0, 0
        return stdout.decode().replace('\r',''), stderr.decode().replace('\r',''), process.returncode, process_duration, process_memory
        
    def __del__(self):
        if os.path.exists(self.folder_name):
            for root, dirs, files in os.walk(self.folder_name, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.folder_name)