from base64 import b64decode

from flask import Flask, request

secret = None
with open('secret.txt') as f:
	secret = f.read()

app = Flask(__name__)

@app.route('/')
def root():
	return '<h1>Hooray!</h1>'

geiger_all = []

@app.route('/geiger/got/<content_b64>', methods= ['POST'])
def geiger_got(content_b64):
	content = b64decode(content_b64.encode('utf-8')).decode('utf-8')
	geiger_all.append(content)
	return f"ok, length {len(content)}"

@app.route('/geiger/viewall')
def geiger_viewall():
	return '<pre>\n' + '\n'.join(geiger_all) + '\n</pre>'
