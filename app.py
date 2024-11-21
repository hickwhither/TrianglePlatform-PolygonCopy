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

}

current_result = {
    "response": None,
    "runtime": None
}

@app.route('/', methods=['GET'])
def home():
    current_status['versions'] = triangle.languages
    return current_status, 200

@app.route('/result')
def result():
    current_result['status'] = current_status['status']
    if current_result['status'] == 'idle': current_result["results"] = triangle.results
    current_result["results_count"] = len(triangle.results or [])
    return current_result, 200

def threading_triangle_judge(data: dict):
    global triangle, current_status, current_result
    current_result["results"] = None
    current_result["runtime"] = None
    current_status["status"] = "compiling"

    startTime = time.time()

    triangle.set_limited(data.get('memory_limit'), data.get('time_limit'))
    triangle.set_tests(data.get('tests'))

    if triangle.force_stop: return

    for i in ['generator', 'brute', 'user']:
        stdout, stderr, returncode = triangle.compile_any(i, data[i].get('source'), data[i].get('language'))
        if returncode != 0:
            current_result["response"] = f"{i} compile error ({returncode})\n" + stdout.decode().replace('\r','') + '\n' + stderr.decode().replace('\r',''),
            current_result["runtime"] = time.time()-startTime
            current_status["status"] = "idle"
            return
        if triangle.force_stop: return
    
    checker = data.get('checker')
    if isinstance(checker, dict):
        stdout, stderr, returncode = triangle.compile_any('checker', checker.get('source'), checker.get('language'))
        if returncode != 0:
            current_result["response"] = f"Checker compile error ({returncode})\n" + stdout.decode().replace('\r','') + '\n' + stderr.decode().replace('\r',''),
            current_result["runtime"] = time.time()-startTime
            current_status["status"] = "idle"
            return
    else:
        response, returncode = triangle.use_builtin_checker(checker)
        if returncode != 0:
            current_result["response"] = f"Checker error ({returncode})\n{response}"
            current_result["runtime"] = time.time()-startTime
            current_status["status"] = "idle"
            return
    if triangle.force_stop: return
    
    current_status["status"] = "judging"
    
    triangle.run(data.get('limit_character', 2690))
    if triangle.force_stop: return
    
    current_result["response"] = "ok"
    current_result["runtime"] = time.time()-startTime
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

    triangle.setup()
    thread = threading.Thread(target=lambda data=data: threading_triangle_judge(data))
    thread.start()

    return {"response": "Judging started"}, 200

@app.route('/stop', methods=['POST'])
def force_stop():
    if current_status["status"] == "idle":
        return {"response": "Judge is already idle"}, 200
    triangle.force_stop = True
    time.sleep(10)
    current_status["response"] = "ok"
    current_status["status"] = "idle"
    current_status["runtime"] = 0
    return {"response": "Judge stopped"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    
    