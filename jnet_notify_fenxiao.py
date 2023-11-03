"""
cron: 00 18 * * *
new Env(' JNET 分销数据');
"""

#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import pymysql
import base64
import hashlib
import hmac
import json
import os
import re
import threading
import time
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

import requests


import sys
sys.path.append(r'../')
from env import *


# 原先的 print 函数和主线程的锁
_print = print
mutex = threading.Lock()


# 定义新的 print 函数
def print(text, *args, **kw):
    """
    使输出有序进行，不出现多线程同一时间输出导致错乱的问题。
    """
    with mutex:
        _print(text, *args, **kw)


# 通知服务
# fmt: off

notify_function = []
# fmt: on

# 首先读取 面板变量 或者 github action 运行变量
for k in push_config:
    if os.getenv(k):
        v = os.getenv(k)
        push_config[k] = v


def bark(title: str, content: str) -> None:
    """
    使用 bark 推送消息。
    """
    if not push_config.get("BARK_PUSH"):
        print("bark 服务的 BARK_PUSH 未设置!!\n取消推送")
        return
    print("bark 服务启动")

    if push_config.get("BARK_PUSH").startswith("http"):
        url = f'{push_config.get("BARK_PUSH")}/{urllib.parse.quote_plus(title)}/{urllib.parse.quote_plus(content)}'
    else:
        url = f'https://api.day.app/{push_config.get("BARK_PUSH")}/{urllib.parse.quote_plus(title)}/{urllib.parse.quote_plus(content)}'

    bark_params = {
        "BARK_ARCHIVE": "isArchive",
        "BARK_GROUP": "group",
        "BARK_SOUND": "sound",
        "BARK_ICON": "icon",
        "BARK_LEVEL": "level",
        "BARK_URL": "url",
    }
    params = ""
    for pair in filter(
        lambda pairs: pairs[0].startswith("BARK_")
        and pairs[0] != "BARK_PUSH"
        and pairs[1]
        and bark_params.get(pairs[0]),
        push_config.items(),
    ):
        params += f"{bark_params.get(pair[0])}={pair[1]}&"
    if params:
        url = url + "?" + params.rstrip("&")
    print(url)
    response = requests.get(url).json()

    if response["code"] == 200:
        print("bark 推送成功！")
    else:
        print("bark 推送失败！")


def console(title: str, content: str) -> None:
    """
    使用 控制台 推送消息。
    """
    print(f"{title}\n\n{content}")


def dingding_bot(title: str, content: str, isMarkdown: bool,TOKEN: str,SECRET: str) -> None:
    """
    使用 钉钉机器人 推送消息。
    """
    if not TOKEN or not SECRET:
        if not push_config.get("DD_BOT_SECRET") or not push_config.get("DD_BOT_TOKEN"):
            print("钉钉机器人 服务的 DD_BOT_SECRET 或者 DD_BOT_TOKEN 未设置!!\n取消推送")
            return
        else:
            TOKEN=push_config.get("DD_BOT_TOKEN")
            SECRET=push_config.get("DD_BOT_SECRET")
    print("钉钉机器人 服务启动")

    timestamp = str(round(time.time() * 1000))
    secret_enc = SECRET.encode("utf-8")
    string_to_sign = "{}\n{}".format(
        timestamp, SECRET)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(
        secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
    ).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = f'https://oapi.dingtalk.com/robot/send?access_token={TOKEN}&timestamp={timestamp}&sign={sign}'
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {"msgtype": "text", "text": {"content": f"{title}\n\n{content}"}}
    if isMarkdown:
        data = {"msgtype": "markdown", "markdown": {
            "title": title, "text": content}}
    response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=15
    ).json()

    if not response["errcode"]:
        print("钉钉机器人 推送成功！")
    else:
        print(url, data, headers, response)
        print("钉钉机器人 推送失败！")


def feishu_bot(title: str, content: str) -> None:
    """
    使用 飞书机器人 推送消息。
    """
    if not push_config.get("FSKEY"):
        print("飞书 服务的 FSKEY 未设置!!\n取消推送")
        return
    print("飞书 服务启动")

    url = f'https://open.feishu.cn/open-apis/bot/v2/hook/{push_config.get("FSKEY")}'
    data = {"msg_type": "text", "content": {"text": f"{title}\n\n{content}"}}
    response = requests.post(url, data=json.dumps(data)).json()

    if response.get("StatusCode") == 0:
        print("飞书 推送成功！")
    else:
        print("飞书 推送失败！错误信息如下：\n", response)


def go_cqhttp(title: str, content: str) -> None:
    """
    使用 go_cqhttp 推送消息。
    """
    if not push_config.get("GOBOT_URL") or not push_config.get("GOBOT_QQ"):
        print("go-cqhttp 服务的 GOBOT_URL 或 GOBOT_QQ 未设置!!\n取消推送")
        return
    print("go-cqhttp 服务启动")

    url = f'{push_config.get("GOBOT_URL")}?access_token={push_config.get("GOBOT_TOKEN")}&{push_config.get("GOBOT_QQ")}&message=标题:{title}\n内容:{content}'
    response = requests.get(url).json()

    if response["status"] == "ok":
        print("go-cqhttp 推送成功！")
    else:
        print("go-cqhttp 推送失败！")


def gotify(title: str, content: str) -> None:
    """
    使用 gotify 推送消息。
    """
    if not push_config.get("GOTIFY_URL") or not push_config.get("GOTIFY_TOKEN"):
        print("gotify 服务的 GOTIFY_URL 或 GOTIFY_TOKEN 未设置!!\n取消推送")
        return
    print("gotify 服务启动")

    url = f'{push_config.get("GOTIFY_URL")}/message?token={push_config.get("GOTIFY_TOKEN")}'
    data = {
        "title": title,
        "message": content,
        "priority": push_config.get("GOTIFY_PRIORITY"),
    }
    response = requests.post(url, data=data).json()

    if response.get("id"):
        print("gotify 推送成功！")
    else:
        print("gotify 推送失败！")


def iGot(title: str, content: str) -> None:
    """
    使用 iGot 推送消息。
    """
    if not push_config.get("IGOT_PUSH_KEY"):
        print("iGot 服务的 IGOT_PUSH_KEY 未设置!!\n取消推送")
        return
    print("iGot 服务启动")

    url = f'https://push.hellyw.com/{push_config.get("IGOT_PUSH_KEY")}'
    data = {"title": title, "content": content}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers).json()

    if response["ret"] == 0:
        print("iGot 推送成功！")
    else:
        print(f'iGot 推送失败！{response["errMsg"]}')


def serverJ(title: str, content: str) -> None:
    """
    通过 serverJ 推送消息。
    """
    if not push_config.get("PUSH_KEY"):
        print("serverJ 服务的 PUSH_KEY 未设置!!\n取消推送")
        return
    print("serverJ 服务启动")

    data = {"text": title, "desp": content.replace("\n", "\n\n")}
    if push_config.get("PUSH_KEY").find("SCT") != -1:
        url = f'https://sctapi.ftqq.com/{push_config.get("PUSH_KEY")}.send'
    else:
        url = f'https://sc.ftqq.com/{push_config.get("PUSH_KEY")}.send'
    response = requests.post(url, data=data).json()

    if response.get("errno") == 0 or response.get("code") == 0:
        print("serverJ 推送成功！")
    else:
        print(f'serverJ 推送失败！错误码：{response["message"]}')


def pushdeer(title: str, content: str) -> None:
    """
    通过PushDeer 推送消息
    """
    if not push_config.get("DEER_KEY"):
        print("PushDeer 服务的 DEER_KEY 未设置!!\n取消推送")
        return
    print("PushDeer 服务启动")
    data = {
        "text": title,
        "desp": content,
        "type": "markdown",
        "pushkey": push_config.get("DEER_KEY"),
    }
    url = "https://api2.pushdeer.com/message/push"
    if push_config.get("DEER_URL"):
        url = push_config.get("DEER_URL")

    response = requests.post(url, data=data).json()

    if len(response.get("content").get("result")) > 0:
        print("PushDeer 推送成功！")
    else:
        print("PushDeer 推送失败！错误信息：", response)


def chat(title: str, content: str) -> None:
    """
    通过Chat 推送消息
    """
    if not push_config.get("CHAT_URL") or not push_config.get("CHAT_TOKEN"):
        print("chat 服务的 CHAT_URL或CHAT_TOKEN 未设置!!\n取消推送")
        return
    print("chat 服务启动")
    data = "payload=" + json.dumps({"text": title + "\n" + content})
    url = push_config.get("CHAT_URL") + push_config.get("CHAT_TOKEN")
    response = requests.post(url, data=data)

    if response.status_code == 200:
        print("Chat 推送成功！")
    else:
        print("Chat 推送失败！错误信息：", response)


def pushplus_bot(title: str, content: str) -> None:
    """
    通过 push+ 推送消息。
    """
    if not push_config.get("PUSH_PLUS_TOKEN"):
        print("PUSHPLUS 服务的 PUSH_PLUS_TOKEN 未设置!!\n取消推送")
        return
    print("PUSHPLUS 服务启动")

    url = "http://www.pushplus.plus/send"
    data = {
        "token": push_config.get("PUSH_PLUS_TOKEN"),
        "title": title,
        "content": content,
        "topic": push_config.get("PUSH_PLUS_USER"),
    }
    body = json.dumps(data).encode(encoding="utf-8")
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, data=body, headers=headers).json()

    if response["code"] == 200:
        print("PUSHPLUS 推送成功！")

    else:
        url_old = "http://pushplus.hxtrip.com/send"
        headers["Accept"] = "application/json"
        response = requests.post(
            url=url_old, data=body, headers=headers).json()

        if response["code"] == 200:
            print("PUSHPLUS(hxtrip) 推送成功！")

        else:
            print("PUSHPLUS 推送失败！")


def qmsg_bot(title: str, content: str) -> None:
    """
    使用 qmsg 推送消息。
    """
    if not push_config.get("QMSG_KEY") or not push_config.get("QMSG_TYPE"):
        print("qmsg 的 QMSG_KEY 或者 QMSG_TYPE 未设置!!\n取消推送")
        return
    print("qmsg 服务启动")

    url = f'https://qmsg.zendee.cn/{push_config.get("QMSG_TYPE")}/{push_config.get("QMSG_KEY")}'
    payload = {
        "msg": f'{title}\n\n{content.replace("----", "-")}'.encode("utf-8")}
    response = requests.post(url=url, params=payload).json()

    if response["code"] == 0:
        print("qmsg 推送成功！")
    else:
        print(f'qmsg 推送失败！{response["reason"]}')


def wecom_app(title: str, content: str) -> None:
    """
    通过 企业微信 APP 推送消息。
    """
    if not push_config.get("QYWX_AM"):
        print("QYWX_AM 未设置!!\n取消推送")
        return
    QYWX_AM_AY = re.split(",", push_config.get("QYWX_AM"))
    if 4 < len(QYWX_AM_AY) > 5:
        print("QYWX_AM 设置错误!!\n取消推送")
        return
    print("企业微信 APP 服务启动")

    corpid = QYWX_AM_AY[0]
    corpsecret = QYWX_AM_AY[1]
    touser = QYWX_AM_AY[2]
    agentid = QYWX_AM_AY[3]
    try:
        media_id = QYWX_AM_AY[4]
    except IndexError:
        media_id = ""
    wx = WeCom(corpid, corpsecret, agentid)
    # 如果没有配置 media_id 默认就以 text 方式发送
    if not media_id:
        message = title + "\n\n" + content
        response = wx.send_text(message, touser)
    else:
        response = wx.send_mpnews(title, content, media_id, touser)

    if response == "ok":
        print("企业微信推送成功！")
    else:
        print("企业微信推送失败！错误信息如下：\n", response)


class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid
        self.ORIGIN = "https://qyapi.weixin.qq.com"
        if push_config.get("QYWX_ORIGIN"):
            self.ORIGIN = push_config.get("QYWX_ORIGIN")

    def get_access_token(self):
        url = f"{self.ORIGIN}/cgi-bin/gettoken"
        values = {
            "corpid": self.CORPID,
            "corpsecret": self.CORPSECRET,
        }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = (
            f"{self.ORIGIN}/cgi-bin/message/send?access_token={self.get_access_token()}"
        )
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {"content": message},
            "safe": "0",
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = (
            f"{self.ORIGIN}/cgi-bin/message/send?access_token={self.get_access_token()}"
        )
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace("\n", "<br/>"),
                        "digest": message,
                    }
                ]
            },
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]


def wecom_bot(title: str, content: str) -> None:
    """
    通过 企业微信机器人 推送消息。
    """
    if not push_config.get("QYWX_KEY"):
        print("企业微信机器人 服务的 QYWX_KEY 未设置!!\n取消推送")
        return
    print("企业微信机器人服务启动")

    origin = "https://qyapi.weixin.qq.com"
    if push_config.get("QYWX_ORIGIN"):
        origin = push_config.get("QYWX_ORIGIN")

    url = f"{origin}/cgi-bin/webhook/send?key={push_config.get('QYWX_KEY')}"
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {"msgtype": "text", "text": {"content": f"{title}\n\n{content}"}}
    response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=15
    ).json()

    if response["errcode"] == 0:
        print("企业微信机器人推送成功！")
    else:
        print("企业微信机器人推送失败！")


def telegram_bot(title: str, content: str) -> None:
    """
    使用 telegram 机器人 推送消息。
    """
    if not push_config.get("TG_BOT_TOKEN") or not push_config.get("TG_USER_ID"):
        print("tg 服务的 bot_token 或者 user_id 未设置!!\n取消推送")
        return
    print("tg 服务启动")

    if push_config.get("TG_API_HOST"):
        url = f"https://{push_config.get('TG_API_HOST')}/bot{push_config.get('TG_BOT_TOKEN')}/sendMessage"
    else:
        url = (
            f"https://api.telegram.org/bot{push_config.get('TG_BOT_TOKEN')}/sendMessage"
        )
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "chat_id": str(push_config.get("TG_USER_ID")),
        "text": f"{title}\n\n{content}",
        "disable_web_page_preview": "true",
    }
    proxies = None
    if push_config.get("TG_PROXY_HOST") and push_config.get("TG_PROXY_PORT"):
        if push_config.get("TG_PROXY_AUTH") is not None and "@" not in push_config.get(
            "TG_PROXY_HOST"
        ):
            push_config["TG_PROXY_HOST"] = (
                push_config.get("TG_PROXY_AUTH")
                + "@"
                + push_config.get("TG_PROXY_HOST")
            )
        proxyStr = "http://{}:{}".format(
            push_config.get("TG_PROXY_HOST"), push_config.get("TG_PROXY_PORT")
        )
        proxies = {"http": proxyStr, "https": proxyStr}
    response = requests.post(
        url=url, headers=headers, params=payload, proxies=proxies
    ).json()

    if response["ok"]:
        print("tg 推送成功！")
    else:
        print("tg 推送失败！")


def aibotk(title: str, content: str) -> None:
    """
    使用 智能微秘书 推送消息。
    """
    if (
        not push_config.get("AIBOTK_KEY")
        or not push_config.get("AIBOTK_TYPE")
        or not push_config.get("AIBOTK_NAME")
    ):
        print("智能微秘书 的 AIBOTK_KEY 或者 AIBOTK_TYPE 或者 AIBOTK_NAME 未设置!!\n取消推送")
        return
    print("智能微秘书 服务启动")

    if push_config.get("AIBOTK_TYPE") == "room":
        url = "https://api-bot.aibotk.com/openapi/v1/chat/room"
        data = {
            "apiKey": push_config.get("AIBOTK_KEY"),
            "roomName": push_config.get("AIBOTK_NAME"),
            "message": {"type": 1, "content": f"【青龙快讯】\n\n{title}\n{content}"},
        }
    else:
        url = "https://api-bot.aibotk.com/openapi/v1/chat/contact"
        data = {
            "apiKey": push_config.get("AIBOTK_KEY"),
            "name": push_config.get("AIBOTK_NAME"),
            "message": {"type": 1, "content": f"【青龙快讯】\n\n{title}\n{content}"},
        }
    body = json.dumps(data).encode(encoding="utf-8")
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, data=body, headers=headers).json()
    print(response)
    if response["code"] == 0:
        print("智能微秘书 推送成功！")
    else:
        print(f'智能微秘书 推送失败！{response["error"]}')

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import pandas as pd
import io
from email.mime.base import MIMEBase
from email import encoders

def smtp(title: str, content: str, json_data: dict = None, SMTP_EMAIL_TO=None, SMTP_NAME_TO=None) -> None:
    """
    使用 SMTP 邮件 推送消息。
    """
    if (
        not push_config.get("SMTP_SERVER")
        or not push_config.get("SMTP_SSL")
        or not push_config.get("SMTP_EMAIL")
        or not push_config.get("SMTP_PASSWORD")
        or not push_config.get("SMTP_NAME")
    ):
        print(
            "SMTP 邮件 的 SMTP_SERVER 或者 SMTP_SSL 或者 SMTP_EMAIL 或者 SMTP_PASSWORD 或者 SMTP_NAME 未设置!!\n取消推送"
        )
        return
    print("SMTP 邮件 服务启动")

    if not SMTP_EMAIL_TO or not SMTP_NAME_TO:
        if not push_config.get("SMTP_EMAIL_TO") or not push_config.get("SMTP_EMAIL_NAME_TO"):
            SMTP_NAME_TO = push_config.get("SMTP_NAME")
            SMTP_EMAIL_TO = push_config.get("SMTP_EMAIL")
        else:
            SMTP_NAME_TO = push_config.get("SMTP_NAME_TO")
            SMTP_EMAIL_TO = push_config.get("SMTP_EMAIL_TO")

    message = MIMEMultipart()
    message["From"] = formataddr(
        (
            Header(push_config.get("SMTP_NAME"), "utf-8").encode(),
            push_config.get("SMTP_EMAIL"),
        )
    )
    message["To"] = formataddr(
        (
            Header(SMTP_NAME_TO, "utf-8").encode(),
            SMTP_EMAIL_TO,
        )
    )
    message["Subject"] = Header(title, "utf-8")

    # 添加正文内容
    message.attach(MIMEText(content, "plain", "utf-8"))

    if json_data:
        try:
            # 将JSON数据转换为DataFrame
            df = pd.DataFrame(json_data)

            # 将DataFrame转换为Excel文件数据
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            excel_data.seek(0)

            # 添加Excel数据作为附件
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(excel_data.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename="data.xlsx"
            )
            message.attach(attachment)
        except Exception as e:
            print(f"转换为Excel并添加附件时出错：{e}")

    try:
        smtp_server = (
            smtplib.SMTP_SSL(push_config.get("SMTP_SERVER"))
            if push_config.get("SMTP_SSL") == "true"
            else smtplib.SMTP(push_config.get("SMTP_SERVER"))
        )
        smtp_server.login(
            push_config.get("SMTP_EMAIL"), push_config.get("SMTP_PASSWORD")
        )
        smtp_server.sendmail(
            push_config.get("SMTP_EMAIL"),
            SMTP_EMAIL_TO,
            message.as_string(),
        )
        smtp_server.close()
        print("SMTP 邮件 推送成功！")
    except Exception as e:
        print(f"SMTP 邮件 推送失败！{e}")
        
def pushme(title: str, content: str) -> None:
    """
    使用 PushMe 推送消息。
    """
    if not push_config.get("PUSHME_KEY"):
        print("PushMe 服务的 PUSHME_KEY 未设置!!\n取消推送")
        return
    print("PushMe 服务启动")

    url = f'https://push.i-i.me/?push_key={push_config.get("PUSHME_KEY")}'
    data = {
        "title": title,
        "content": content,
    }
    response = requests.post(url, data=data)

    if response.status_code == 200 and response.text == "success":
        print("PushMe 推送成功！")
    else:
        print(f"PushMe 推送失败！{response.status_code} {response.text}")


def chronocat(title: str, content: str) -> None:
    """
    使用 CHRONOCAT 推送消息。
    """
    if (
        not push_config.get("CHRONOCAT_URL")
        or not push_config.get("CHRONOCAT_QQ")
        or not push_config.get("CHRONOCAT_TOKEN")
    ):
        print("CHRONOCAT 服务的 CHRONOCAT_URL 或 CHRONOCAT_QQ 未设置!!\n取消推送")
        return

    print("CHRONOCAT 服务启动")

    user_ids = re.findall(r"user_id=(\d+)", push_config.get("CHRONOCAT_QQ"))
    group_ids = re.findall(r"group_id=(\d+)", push_config.get("CHRONOCAT_QQ"))

    url = f'{push_config.get("CHRONOCAT_URL")}/api/message/send'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {push_config.get("CHRONOCAT_TOKEN")}',
    }

    for chat_type, ids in [(1, user_ids), (2, group_ids)]:
        if not ids:
            continue
        for chat_id in ids:
            data = {
                "peer": {"chatType": chat_type, "peerUin": chat_id},
                "elements": [
                    {
                        "elementType": 1,
                        "textElement": {"content": f"{title}\n\n{content}"},
                    }
                ],
            }
            response = requests.post(
                url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                if chat_type == 1:
                    print(f"QQ个人消息:{ids}推送成功！")
                else:
                    print(f"QQ群消息:{ids}推送成功！")
            else:
                if chat_type == 1:
                    print(f"QQ个人消息:{ids}推送失败！")
                else:
                    print(f"QQ群消息:{ids}推送失败！")


def parse_headers(headers):
    if not headers:
        return {}

    parsed = {}
    lines = headers.split("\n")

    for line in lines:
        i = line.find(":")
        if i == -1:
            continue

        key = line[:i].strip().lower()
        val = line[i + 1:].strip()
        parsed[key] = parsed.get(key, "") + ", " + \
            val if key in parsed else val

    return parsed


def parse_body(body, content_type):
    if not body:
        return ""

    parsed = {}
    lines = body.split("\n")

    for line in lines:
        i = line.find(":")
        if i == -1:
            continue

        key = line[:i].strip().lower()
        val = line[i + 1:].strip()

        if not key or key in parsed:
            continue

        try:
            json_value = json.loads(val)
            parsed[key] = json_value
        except:
            parsed[key] = val

    if content_type == "application/x-www-form-urlencoded":
        data = urlencode(parsed, doseq=True)
        return data

    if content_type == "application/json":
        data = json.dumps(parsed)
        return data

    return parsed


def format_notify_content(url, body, title, content):
    if "$title" not in url and "$title" not in body:
        return {}

    formatted_url = url.replace("$title", urllib.parse.quote_plus(title)).replace(
        "$content", urllib.parse.quote_plus(content)
    )
    formatted_body = body.replace("$title", title).replace("$content", content)

    return formatted_url, formatted_body


def custom_notify(title: str, content: str) -> None:
    """
    通过 自定义通知 推送消息。
    """
    if not push_config.get("WEBHOOK_URL") or not push_config.get("WEBHOOK_METHOD"):
        print("自定义通知的 WEBHOOK_URL 或 WEBHOOK_METHOD 未设置!!\n取消推送")
        return

    print("自定义通知服务启动")

    WEBHOOK_URL = push_config.get("WEBHOOK_URL")
    WEBHOOK_METHOD = push_config.get("WEBHOOK_METHOD")
    WEBHOOK_CONTENT_TYPE = push_config.get("WEBHOOK_CONTENT_TYPE")
    WEBHOOK_BODY = push_config.get("WEBHOOK_BODY")
    WEBHOOK_HEADERS = push_config.get("WEBHOOK_HEADERS")

    formatUrl, formatBody = format_notify_content(
        WEBHOOK_URL, WEBHOOK_BODY, title, content
    )

    if not formatUrl and not formatBody:
        print("请求头或者请求体中必须包含 $title 和 $content")
        return

    headers = parse_headers(WEBHOOK_HEADERS)
    body = parse_body(formatBody, WEBHOOK_CONTENT_TYPE)
    response = requests.request(
        method=WEBHOOK_METHOD, url=formatUrl, headers=headers, timeout=15, data=body
    )

    if response.status_code == 200:
        print("自定义通知推送成功！")
    else:
        print(f"自定义通知推送失败！{response.status_code} {response.text}")


def one() -> str:
    """
    获取一条一言。
    :return:
    """
    url = "https://v1.hitokoto.cn/"
    res = requests.get(url).json()
    return res["hitokoto"] + "    ----" + res["from"]


if push_config.get("BARK_PUSH"):
    notify_function.append(bark)
if push_config.get("CONSOLE"):
    notify_function.append(console)
if push_config.get("DD_BOT_TOKEN") and push_config.get("DD_BOT_SECRET"):
    notify_function.append(dingding_bot)
if push_config.get("FSKEY"):
    notify_function.append(feishu_bot)
if push_config.get("GOBOT_URL") and push_config.get("GOBOT_QQ"):
    notify_function.append(go_cqhttp)
if push_config.get("GOTIFY_URL") and push_config.get("GOTIFY_TOKEN"):
    notify_function.append(gotify)
if push_config.get("IGOT_PUSH_KEY"):
    notify_function.append(iGot)
if push_config.get("PUSH_KEY"):
    notify_function.append(serverJ)
if push_config.get("DEER_KEY"):
    notify_function.append(pushdeer)
if push_config.get("CHAT_URL") and push_config.get("CHAT_TOKEN"):
    notify_function.append(chat)
if push_config.get("PUSH_PLUS_TOKEN"):
    notify_function.append(pushplus_bot)
if push_config.get("QMSG_KEY") and push_config.get("QMSG_TYPE"):
    notify_function.append(qmsg_bot)
if push_config.get("QYWX_AM"):
    notify_function.append(wecom_app)
if push_config.get("QYWX_KEY"):
    notify_function.append(wecom_bot)
if push_config.get("TG_BOT_TOKEN") and push_config.get("TG_USER_ID"):
    notify_function.append(telegram_bot)
if (
    push_config.get("AIBOTK_KEY")
    and push_config.get("AIBOTK_TYPE")
    and push_config.get("AIBOTK_NAME")
):
    notify_function.append(aibotk)
if (
    push_config.get("SMTP_SERVER")
    and push_config.get("SMTP_SSL")
    and push_config.get("SMTP_EMAIL")
    and push_config.get("SMTP_PASSWORD")
    and push_config.get("SMTP_NAME")
):
    notify_function.append(smtp)
if push_config.get("PUSHME_KEY"):
    notify_function.append(pushme)
if (
    push_config.get("CHRONOCAT_URL")
    and push_config.get("CHRONOCAT_QQ")
    and push_config.get("CHRONOCAT_TOKEN")
):
    notify_function.append(chronocat)
if push_config.get("WEBHOOK_URL") and push_config.get("WEBHOOK_METHOD"):
    notify_function.append(custom_notify)


def send(title: str, content: str) -> None:
    if not content:
        print(f"{title} 推送内容为空！")
        return

    # 根据标题跳过一些消息推送，环境变量：SKIP_PUSH_TITLE 用回车分隔
    skipTitle = os.getenv("SKIP_PUSH_TITLE")
    if skipTitle:
        if title in re.split("\n", skipTitle):
            print(f"{title} 在SKIP_PUSH_TITLE环境变量内，跳过推送！")
            return

    hitokoto = push_config.get("HITOKOTO")

    text = one() if hitokoto else ""
    content += "\n\n" + text

    ts = [
        threading.Thread(target=mode, args=(
            title, content), name=mode.__name__)
        for mode in notify_function
    ]
    [t.start() for t in ts]
    [t.join() for t in ts]


# =========================================================================================


# from Conf import *


class MySQLTool:
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()

    def execute_query(self, query, params=None):
        self.connect()
        self.cursor.execute(query, params)
        result = self.cursor.fetchall()
        self.connection.commit()
        self.close()
        return result

    def execute_update(self, query, params=None):
        self.connect()
        self.cursor.execute(query, params)
        self.connection.commit()
        self.close()

    def close(self):
        self.cursor.close()
        self.connection.close()


def select(cfg, sql, params=None):
    # 创建MySQLTool实例
    my_tool = MySQLTool(DB_HOST, DB_USER,  DB_PASSWORD, DB_DATABASE)
    result = my_tool.execute_query(sql, params)
    if len(result) == 0:
        return []
    rows = []
    for ri in range(len(result)):
        r = {
            '_id_': ri+1
        }
        for i in range(len(cfg)):
            r[cfg[i]] = result[ri][i]
        rows.append(r)
    return rows


def formatMarkdown(rows, config=None):
    formatStr = ''
    if len(rows) == 0:
        return formatStr
    if not config:
        config = {}
        for k in rows[0]:
            config[k] = k
    formatStr += '| ' + ' | '.join([config[k] for k in config]) + ' |\n'
    formatStr += '| ' + ' | '.join(['---' for _ in config]) + ' |\n'
    for row in rows:
        formatStr += '| ' + ' | '.join([str(row[k]) for k in config]) + ' |\n'
    return formatStr

# =========================================================================================

def main():
    DB_SQL='''select p.product_barcode,  count(1) cnt,ba.ib_quantity  qty
    from     wms.orders o
            left join order_product p on o.order_id = p.order_id
            inner join (select product_id,sum(ib_quantity) ib_quantity from inventory_batch group by product_id) ba on p.product_id = ba.product_id
    where
    order_status = 8 and (remark = 'vicky_fx' or remark = '2158-fx' )
    group by p.product_barcode order by 3'''
    DB_SELECTED_FIELD = ['product_barcode', 'cnt', 'qty']
    rowsA = select(DB_SELECTED_FIELD, DB_SQL)
    dingding_bot("分销清单", "![](https://img.shields.io/badge/%F0%9F%A7%BE-%20%E5%88%86%E9%94%80%E6%B8%85%E5%8D%95-FFDD67.svg?style=flat-square)\n"+formatMarkdown(rowsA, {
        '_id_': '序号',
        'product_barcode': '商品条码',
        'cnt': '分销数量',
        'qty': '库存数量'
    }), True,None,None)


if __name__ == "__main__":
    main()

