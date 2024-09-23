from base64 import b64decode
import collections, time

from flask import Flask, request

secret = None
with open('secret.txt') as f:
	secret = f.read().strip()

app = Flask(__name__)

@app.route('/')
def root():
	return '<h1>Hooray!</h1>'

geiger_all = collections.deque()
SAVE_DURATION_SECS = 10

class Entry:
	__slots__ = ['ts', 'count']

	def __init__(self, ts: float, count: int):
		self.ts = ts
		self.count = count
	
	def __str__(self):
		return f'[Entry of {self.count} count(s) at {self.ts}]'

@app.route('/geiger/got/<content_b64>', methods= ['POST'])
def geiger_got(content_b64):
	if 'X-Shared-Secret' not in request.headers:
		return "err, no secret", 400
	if request.headers['X-Shared-Secret'] != secret:
		return "err, bad secret", 401
	content = b64decode(content_b64.encode('utf-8')).decode('utf-8')
	num = int(content.strip())
	now = time.time()
	geiger_all.append(Entry(now, num))
	last_preserved = now - SAVE_DURATION_SECS
	n_purged = 0
	while True:
		if geiger_all[0].ts < last_preserved:
			geiger_all.popleft()
			n_purged += 1
		else:
			break
	return f"ok, stored {num} purged {n_purged}"

@app.route('/geiger/viewall')
def geiger_viewall():
	return '<pre>\n' + '\n'.join([ str(i) for i in geiger_all ]) + '\n</pre>'
