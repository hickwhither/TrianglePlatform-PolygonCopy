from flask import Flask, request
import os, threading, sys
import zipfile, shutil
import time

from triangle import Triangle

app = Flask(__name__)
triangle:Triangle = Triangle()

current_status = {
    "status": "idle",
    "start": time.time(),

    "response": None,
    "results": None,
    "runtime": None
}

triangle.languages
"""
{
    "id": "python3",
    "file_extension": ".py",
    "compilation": null,
    "execution": "python {name}.py",
    "version": "python -V"
}   
"""

@app.route('/', methods=['GET'])
def home():
    current_status["results"] = triangle.results
    return current_status, 200

def threading_triangle_judge(data: dict):
    global triangle, current_status
    current_status["response"] = None
    current_status["results"] = None
    current_status["runtime"] = None
    current_status["status"] = "compiling"

    startTime = time.time()

    triangle.set_limited(data.get('memory_limit'), data.get('time_limit'))
    triangle.set_tests(data.get('tests'))

    for i in ['generator', 'brute', 'user']:
        stdout, stderr, returncode = triangle.compile_any(i, data[i].get('source'), data[i].get('language'))
        if returncode != 0:
            current_status["response"] = f"{i} compile error ({returncode})\n" + stdout.decode().replace('\r','') + '\n' + stderr.decode().replace('\r',''),
            current_status["runtime"] = time.time()-startTime
            current_status["status"] = "idle"
            return
    checker = data.get('checker')
    if isinstance(checker, dict):
        stdout, stderr, returncode = triangle.compile_any('checker', checker.get('source'), checker.get('language'))
        if returncode != 0:
            current_status["response"] = f"Checker compile error ({returncode})\n" + stdout.decode().replace('\r','') + '\n' + stderr.decode().replace('\r',''),
            current_status["runtime"] = time.time()-startTime
            current_status["status"] = "idle"
            return
    else:
        response, returncode = triangle.use_builtin_checker(checker)
        if returncode != 0:
            current_status["response"] = f"Checker error ({returncode})\n{response}"
            current_status["runtime"] = time.time()-startTime
            current_status["status"] = "idle"
            return
    
    current_status["status"] = "judging"
    
    triangle.run(data.get('limit_character', 2690))
    verdicts = {}
    for i in triangle.results:
        if not verdicts.get(i['verdict']): verdicts[i['verdict']] = 0
        verdicts[i['verdict']] += 1
    verdict_max = max(verdicts, key=verdicts.get)
    
    current_status["response"] = "ok"
    current_status["runtime"] = time.time()-startTime
    current_status["status"] = "idle"

@app.route('/judge', methods=['POST'])
def triangle_judge():
    if current_status["status"] != "idle":
            return {"response": "Judge is busy"}, 503

    data = request.get_json()

    if not isinstance(data.get('tests'), list):
        return {"response": "Invalid 'tests' format. Expected a list."}, 400

    try:
        float(data.get('memory_limit'))
        float(data.get('time_limit'))
    except:
        return {"response": "Invalid 'memory_limit' or 'time_limit' format. Expected float values."}, 400

    def has_required_keys(d):
        return isinstance(d, dict) and all(key in d for key in ['source', 'language'])
    for key in ['generator', 'brute', 'user']:
        if not has_required_keys(data.get(key)):
            return {"response": f"Invalid `{key}` format. Expected a dictionary with 'source' and 'language' keys."}, 400

    checker = data.get('checker')
    if not (has_required_keys(checker) or (isinstance(checker, str) and checker.startswith(('token', 'line', 'float')))):
        return {"response": "Invalid 'checker' format. Expected a dictionary with 'source' and 'language' keys or a string starting with 'token', 'line', or 'float'."}, 400

    
    thread = threading.Thread(target=lambda data=data: threading_triangle_judge(data))
    thread.start()

    return {"response": "Judging started"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    
    