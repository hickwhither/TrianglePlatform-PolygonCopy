from flask import Flask, request
import os, threading, sys
import zipfile, shutil
import time
SECRET = sys.agrv[1]

from judger import *

app = Flask(__name__)
triangle = Triangle()
usercode = SourceCode(triangle)


idk_what_to_name_this = {
    "start": time.time(),
    "status": "idle",
}

submissions_result = {
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

@app.route('/submissions', methods=['GET'])
def submissions():
    if request.headers.get('Authorization') != SECRET:
        return {"error": "Unauthorized"}, 401
    return submissions_result, 200

def judge_go_brr_lmao(code, language):
    global submissions_result
    idk_what_to_name_this['status'] = "Compiling tests"
    try:
        triangle.compile()
    except InternalError as e:
        submissions_result = {
            "response": str(e),
            "results": None
        }
        return
    idk_what_to_name_this['status'] = "Compiling solution"
    stdout, stderr, returncode = usercode.compile(code, language)
    if returncode:
        submissions_result = {
            "response": "Compile Error\n" + stdout + '\n' + stderr,
            "results": None
        }
        return
    idk_what_to_name_this['status'] = "Judging"
    triangle.run(usercode)
    submissions_result = {
        "response": stdout + '\n' + stderr,
        "results": triangle.results
    }
    idk_what_to_name_this['status'] = "idle"

@app.route('/judge', methods=['POST'])
def judge():
    if request.headers.get('Authorization') != SECRET:
        return {"error": "Unauthorized"}, 401
    
    if 'code' not in request.form or 'language' not in request.form:
        return {"error": "Missing code or language parameters"}, 400
    code = request.form['code']
    language = request.form['language']
    
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    file = request.files['file']
    if file.filename == '':
        return {"error": "No file selected"}, 400
    if not file.filename.endswith('.zip'):
        return {"error": "File must be a zip file"}, 400
    
    for filename in os.listdir('workspace'):
        file_path = os.path.join('workspace', filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

    filename = file.filename
    file.save(os.path.join('workspace', filename))   

    with zipfile.ZipFile(os.path.join('workspace', filename), 'r') as zip_ref:
        zip_ref.extractall('workspace')
    
    thread = threading.Thread(target=judge_go_brr_lmao, args=(code, language))
    thread.start()

    return {"status": "Judging started"}, 200

if __name__ == '__main__':
    app.run()
    
    