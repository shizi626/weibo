# encoding=utf-8
import json
import base64
import requests
import logging
import sys


myWeiBo = [
    {'no': "qz2suvgkcuxge@qq.com", 'psw': "fast3211"},

]


def getCookies(account,password):
    """ 获取Cookies """
    loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
    username = base64.b64encode(account.encode('utf-8')).decode('utf-8')
    postData = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }
    session = requests.Session()
    r = session.post(loginURL, data=postData)
    jsonStr = r.content.decode('gbk')
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        print "Get Cookie Success!( Account:%s )" % account
        cookie = session.cookies.get_dict()
        return cookie

def updateCookie(fail_cookie):
    fail_account = [x[0] for x in cookies.items() if fail_cookie in x[1]]
    password = myWeiBo[fail_account]
    cookie = getCookies(fail_account, password)
    cookies[fail_account] = cookie
    print "update finished."

def initCookie(weibo):
    cookies = {}
    for elem in weibo:
        account = elem['no']
        password = elem['psw']
        cookie = getCookies(account, password)
        cookies[account] = cookie
    if cookies == None:
        print "no cookies Success at all!"
        sys.exit()
    else:
        return cookies

cookies = initCookie(myWeiBo)
print "Get Cookies Finish!( Num:%d)" % len(cookies)