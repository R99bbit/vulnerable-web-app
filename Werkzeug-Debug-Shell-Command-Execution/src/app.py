from flask import Flask, request
import os
import uuid

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!!'

@app.route('/getImage')
def getImage():
    param = request.args.to_dict()
    if len(param) == 0:
        return 'error.'
    if 'filename' not in param.keys():
        return 'error.'

    filename = './assets/image/' + param['filename']
    filename = filename.replace('../', '')
    try:
        print(filename)
        f = open(filename, 'rb')
        res = f.read()
        f.close()
    except Exception as e:
        print(e)
        return 'error.'

    return res

@app.route('/add')
def add():
    try:
        param = request.args.to_dict()
        arg1 = int(param['arg1'])
        arg2 = int(param['arg2'])
        res = arg1 + arg2
        res = "result : " + str(res)
        return res
    except:
        return "error."

@app.route('/sub')
def sub():
    try:
        param = request.args.to_dict()
        arg1 = int(param['arg1'])
        arg2 = int(param['arg2'])
        res = arg1 - arg2
        res = "result : " + str(res)
        return res
    except:
        return "error."

@app.route('/mul')
def mul():
    try:
        param = request.args.to_dict()
        arg1 = int(param['arg1'])
        arg2 = int(param['arg2'])
        res = arg1 * arg2
        res = "result : " + str(res)
        return res
    except:
        return "error."

@app.route('/div')
def div():
    try:
        param = request.args.to_dict()
        arg1 = int(param['arg1'])
        arg2 = int(param['arg2'])
    except:
        return "error."
    res = arg1 / arg2
    res = "result : " + str(res)
    return res

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)