#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import requests
import time

url = "http://0.0.0.0:8080"
# 群号
target = 1111111111
# bot的QQ号
admin_qq = 1111111111
# 管理员的QQ号，用于监控bot
bot_qq = 1111111111
# make sending interval more than 1.1s
last_send_time = 0


def message(message: str, type=0):
	if type == 0:
		data = {
            "ToUserUid": target,
            "SendToType": 2,
			"SendMsgType": "TextMsg",
            "Content": message
		}
	else:
		data = {
            "ToUserUid": admin_qq,
            "SendToType": 1,
			"SendMsgType": "TextMsg",
            "Content": message
		}
	global last_send_time
	if time.time() - last_send_time < 1.1:
		time.sleep(1.1 - time.time() + last_send_time)
	r = requests.post(url + "?qq=" + str(bot_qq) + "&funcname=SendMsgV2", json.dumps(data))
	last_send_time = time.time()
	print(data)
	if json.loads(r.text).get('Ret') != 0:
		print("message sending failed.")
		print(r.text)
		return
	print("message sending succeeded")
    # print(r.text)
