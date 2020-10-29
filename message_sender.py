#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import requests

url = "http://0.0.0.0:8080"
# 群号
target = 1111111111
# bot的QQ号
admin_qq = 1111111111
# 管理员的QQ号，用于监控bot
bot_qq = 1111111111


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
	r = requests.post(url + "?qq=" + str(bot_qq) + "&funcname=SendMsgV2", json.dumps(data))
	print(data)
	if json.loads(r.text).get('Ret') != 0:
		print("message sending failed.")
		print(r.text)
		return
	print("message sending succeeded")
    # print(r.text)
