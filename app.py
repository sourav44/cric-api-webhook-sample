
#info={'pid':35320,'apikey':'WNHTx5ihhIafnXoE62PW6NLn7zL2'}
#req=requests.get('http://cricapi.com/api/playerStats',params=(info));
#request=json.loads(req.text);
#pprint(request);

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import requests
import csv

from flask import Flask
from flask import request
from flask import make_response

from pprint import pprint


# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "PlayerStats":
        return {}
    pid= generate_pid(req);
    if pid is None:
        return {}
    info={'pid':pid,'apikey':'WNHTx5ihhIafnXoE62PW6NLn7zL2'}
    result=requests.get('http://cricapi.com/api/playerStats',params=(info));
    data = json.loads(result.text)
    res = makeWebhookResult(data,req)
    return res


def generate_pid(req):
	result = req.get("result")
	parameters = result.get("parameters")
	player_name = parameters.get("PlayerData")
	if player_name is None:
		return None
	with open('PlayerData.csv', 'rt') as f:
		reader = csv.reader(f, delimiter=',')
		for row in reader: 
			if(row[0]==player_name):
				pid=row[1]      
	if pid is None:
		return None
	return pid

def makeWebhookResult(data,res):
    form=res["result"]["parameters"]["format"]
    query=res["result"]["parameters"]["Stats"]
    if form is None:
        return {}
    if query is None:
        return {}
    stats = data.get("data")
    if stats is None:
        return {}
    if query=='Runs'or query=='SR' or query=='ave' or query=='Ct':
       sol=stats["batting"][form][query]
    elif query=='Wkts' or query=='econ':
       sol=stats["bowling"][form][query]
    else :
       sol=data['majorTeams']
    if sol is None:
        return {}
 
    speech = data['fullName']+" has the following stats in "+form+": "+query+": "+sol

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "cric-api-webhook-sample"
    }


if __name__ == '__main__':
	port = int(os.getenv('PORT', 5000))

	print("Starting app on port %d" % port)

	app.run(debug=False,Port=port,host='0.0.0.0')