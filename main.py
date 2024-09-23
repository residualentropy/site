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

geiger_cpm = collections.deque()
SAVED_DURATION_SECS = 50
CPM_PERIOD_SECS = 5

class Entry:
	__slots__ = ['ts_start', 'cpm']

	def __init__(self, ts_start: float, cpm: float):
		self.ts_start = ts_start
		self.cpm = cpm
	
	def __str__(self):
		ts_end = self.ts_start + CPM_PERIOD_SECS
		return f'[Entry: {self.cpm} CPM from {self.ts_start} to {ts_end}*]'

@app.route('/geiger/got/<content_b64>', methods= ['POST'])
def geiger_got(content_b64):
	if 'X-Shared-Secret' not in request.headers:
		return "err, no secret", 400
	if request.headers['X-Shared-Secret'] != secret:
		return "err, bad secret", 401
	content = b64decode(content_b64.encode('utf-8')).decode('utf-8')
	[period_start_time, cpm] = [
		float(i)
		for i in content.strip().split(',')
	]
	geiger_cpm.append(Entry(period_start_time, cpm))
	msg = f'recieved: (cpm: {cpm} period_start_time: {period_start_time})'
	n_purged = 0
	while len(geiger_cpm) > 0:
		if geiger_cpm[0].ts_start < (period_start_time - SAVED_DURATION_SECS):
			geiger_cpm.popleft()
			n_purged += 1
		else:
			break
	msg += f', purged {n_purged}'
	return f'ok, {msg}'

@app.route('/geiger/cpm.json')
def geiger_view_cpm():
	return {
		"ts_start": [ entry.ts_start for entry in geiger_cpm ],
		"cpm": [ entry.cpm for entry in geiger_cpm ],
	}
