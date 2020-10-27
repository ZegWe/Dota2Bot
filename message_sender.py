#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import requests

url = "http://127.0.0.1:8080"
# 群号
target = 1111111111
# bot的QQ号
bot_qq = 1111111111
# mirai http的auth key
authKey = "xxxxxxx"


def message(message: list, type=0):
    # Authorize
	auth_key = {"authKey": authKey}
	r = requests.post(url + "/auth", json.dumps(auth_key))
	if json.loads(r.text).get('code') != 0:
		print("ERROR@auth")
		print(r.text)
		exit(1)
    # Verify
	session_key = json.loads(r.text).get('session')
	session = {"sessionKey": session_key, "qq": bot_qq}
	r = requests.post(url + "/verify", json.dumps(session))
	if json.loads(r.text).get('code') != 0:
		print("ERROR@verify")
		print(r.text)
		exit(2)
	if type == 0:
		data = {
            "sessionKey": session_key,
            "target": target,
            "messageChain": message
		}
	else:
		data = {
            "sessionKey": session_key,
            "target": 1278300305,
            "messageChain": message
		}
	if type == 0:
		r = requests.post(url + "/sendGroupMessage", json.dumps(data))
	# release
	else:
		r = requests.post(url + "/sendFriendMessage", json.dumps(data))
	if json.loads(r.text).get('code') != 0:
		print("message sending failed.")
	data = {
			"sessionKey": session_key,
            "qq": bot_qq
        }
	r = requests.post(url + "/release", json.dumps(data))
    # print(r.text)
