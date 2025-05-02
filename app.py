import os
import json
import requests
import subprocess
from time import sleep

from os.path import join, dirname
from dotenv import load_dotenv

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# from gpiozero import LED

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

IR_send_denki_path = join(dirname(__file__), 'IR_send_denki.py')

# infrared command for denki
argsDenkiOnCh1 = ['python3', IR_send_denki_path, '-c', 'denki_on_ch1']
argsDenkiOnCh2 = ['python3', IR_send_denki_path, '-c', 'denki_on_ch2']
argsDenkiOffCh1 = ['python3', IR_send_denki_path, '-c', 'denki_off_ch1']
argsDenkiOffCh2 = ['python3', IR_send_denki_path, '-c', 'denki_off_ch2']

denki_ch1_switch = 0
denki_ch2_switch = 0

# raspberrypi shutdown command
argsShutdown = ['sudo', 'poweroff']

# LINE Messaging API Information
url = "https://api.line.me/v2/bot/message/reply"
lineToken = os.environ.get("LINE_TOKEN")
headers = {"Content-Type": "application/json", "Authorization": "Bearer " + lineToken}

# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def check_temp_and_hum_data():
    json_filename = "temp_and_hum_data.json"
    with open(json_filename, "r") as f:
        data = json.load(f)

    return data['temp'], data['hum']

@app.message()
def action(message, say):
    global denki_ch1_switch
    global denki_ch2_switch
    state = ""

    textDict = json.loads(message['text'])
    print(f"メッセージ：{textDict['message']['text']}")
    print(f"ReplyToken：{textDict['replyToken']}")

    commandMsg = textDict['message']['text']
    replyToken = textDict['replyToken']

    if commandMsg == "denki_ch1_on":
        pro = subprocess.Popen(argsDenkiOnCh1)
        denki_ch1_switch = 1
        state = "on"

    elif commandMsg == "denki_ch1_off":
        pro = subprocess.Popen(argsDenkiOffCh1)
        denki_ch1_switch = 0
        state = "off"

    elif commandMsg == "denki_ch2_on":
        pro = subprocess.Popen(argsDenkiOnCh2)
        denki_ch2_switch = 1
        state = "on"

    elif commandMsg == "denki_ch2_off":
        pro = subprocess.Popen(argsDenkiOffCh2)
        denki_ch2_switch = 0
        state = "off"

    elif commandMsg == "poweroff":
        pro = subprocess.Popen(argsShutdown)
        state = "shutdown"

    elif commandMsg == "temp_and_hum_check":
        temp, hum = check_temp_and_hum_data()

    else:
        state = "none"
        pass
        
    msgText = f"send {commandMsg} command"
    if commandMsg == "temp_and_hum_check":
        msgText = f"temp:{temp} degC \n hum:{hum} %"

    contents = {"replyToken": replyToken, "messages" :[{"type": "text", "text" : msgText}]}

    res = requests.post(url, headers=headers, json=contents).json()

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

