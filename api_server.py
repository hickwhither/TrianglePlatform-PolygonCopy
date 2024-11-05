from flask import Flask, request
import os, threading, sys
import zipfile, shutil
import time
SECRET = sys.argv[1]

from triangle import Triangle

app = Flask(__name__)
triangle:Triangle = Triangle()

idk_what_to_name_this = {
    "start": time.time(),
    "status": "idle",
}

submission_result = {
    "response": None,
    "results": None
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
    if request.headers.get('Authorization') != SECRET:
        return {"error": "Unauthorized"}, 401
    return idk_what_to_name_this, 200

@app.route('/submission', methods=['GET'])
def submission():
    if request.headers.get('Authorization') != SECRET:
        return {"error": "Unauthorized"}, 401
    return submission_result, 200

def threading_triangle_judge(data: dict):
    global triangle, idk_what_to_name_this, submission_result
    startTime = time.time()

    triangle.set_limited(data.get('memory_limit'), data.get('time_limit'))

    triangle.set_tests(data.get('tests'))

    for i in ['generator', 'solver', 'user']:
        stdout, stderr, returncode = triangle.compile_any(i, data[i].get('source'), data[i].get('language'))
        if returncode != 0:
            submission_result = {
                "response": f"{i} compile error ({returncode})\n{stdout.decode().replace('\r','')}{stderr.decode().replace('\r','')}",
                "verdict": 69,
                "results": None,
                "runtime": time.time()-startTime
            }
    
    checker = data.get('checker')
    if isinstance(checker, dict):
        stdout, stderr, returncode = triangle.compile_any('checker', checker.get('source'), checker.get('language'))
        if returncode != 0:
            submission_result = {
                "response": f"Checker compile error ({returncode})\n{stdout.decode().replace('\r','')}{stderr.decode().replace('\r','')}",
                "verdict": 69,
                "results": None,
                "runtime": time.time()-startTime
            }
            return
    else:
        response, returncode = triangle.use_builtin_checker(checker)
        if returncode != 0:
            submission_result = {
                "response": f"Checker error ({returncode})\n{response}",
                "verdict": 69,
                "results": None,
        "runtime": time.time()-startTime
            }
            return
    
    triangle.run()
    submission_result = {
        "response": "ok",
        "verdict": max(i for i, result in enumerate(triangle.results) if result['verdict'] == max(r['verdict'] for r in triangle.results)),
        "results": triangle.results,
        "runtime": time.time()-startTime
    }

@app.route('/triangle_judge', methods=['POST'])
def triangle_judge():
    if request.headers.get('Authorization') != SECRET:
        return {"error": "Unauthorized"}, 401
    
    data = request.get_json()

    if not isinstance(data.get('tests'), list):
        return {"error": "Invalid 'tests' format. Expected a list."}, 400

    try:
        float(data.get('memory_limit'))
        float(data.get('time_limit'))
    except:
        return {"error": "Invalid 'memory_limit' or 'time_limit' format. Expected float values."}, 400

    def has_required_keys(d):
        return isinstance(d, dict) and all(key in d for key in ['source', 'language'])
    for key in ['generator', 'solver', 'user']:
        if not has_required_keys(data.get(key)):
            return {"error": f"Invalid '{key}' format. Expected a dictionary with 'source' and 'language' keys."}, 400

    checker = data.get('checker')
    if not (has_required_keys(checker) or (isinstance(checker, str) and checker.startswith(('token', 'line', 'float')))):
        return {"error": "Invalid 'checker' format. Expected a dictionary with 'source' and 'language' keys or a string starting with 'token', 'line', or 'float'."}, 400

    
    thread = threading.Thread(target=lambda data=data: threading_triangle_judge(data))
    thread.start()

    return {"status": "Judging started"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
    
    