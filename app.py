import os
import json
import requests
import subprocess
from time import sleep

from os.path import join, dirname
from dotenv import load_dotenv

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# setup for cloudinary uploader
import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api

IR_send_denki_path = join(dirname(__file__), 'IR_send_denki.py')
IR_send_air_path = join(dirname(__file__), 'IR_send_air.py')

# infrared command for denki
argsDenkiOnCh1 = ['python3', IR_send_denki_path, '-c', 'denki_on_ch1']
argsDenkiOnCh2 = ['python3', IR_send_denki_path, '-c', 'denki_on_ch2']
argsDenkiOffCh1 = ['python3', IR_send_denki_path, '-c', 'denki_off_ch1']
argsDenkiOffCh2 = ['python3', IR_send_denki_path, '-c', 'denki_off_ch2']

# infrared command for air
argsAirOn = ['python3', IR_send_air_path, '-c', 'reibo_on_260']

denki_ch1_switch = 0
denki_ch2_switch = 0
air_switch = 0

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

def one_shot():
   command_text = "libcamera-jpeg --output /home/ayusan/IR_air/images/test2.jpeg -n --width 1200 --height 800"
   command_list = command_text.split(" ")
   pro = subprocess.Popen(command_list)

   while pro.poll() is None:
       sleep(1)

def upload_image():
    upload = cloudinary.uploader.upload("/home/ayusan/IR_air/images/test2.jpeg", public_id="room_picture", unique_filename=False, overwrite=True, invalidate=True)
    secure_url = upload["secure_url"]
    
    return secure_url

@app.message()
def action(message, say):
    global denki_ch1_switch
    global denki_ch2_switch
    global air_switch
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

    elif commandMsg == "reibo_on_260":
        pro = subprocess.Popen(argsAirOn)
        air_switch = 1
        state = "air on"
    
    elif commandMsg == "check_room":
        one_shot()
        secure_url = upload_image()

    else:
        state = "none"
        pass
        
    if commandMsg == "temp_and_hum_check":
        msgText = f"temp:{temp} degC \n hum:{hum} %"
    else:
        msgText = f"send {commandMsg} command"
    
    if commandMsg == "check_room":
        contents = {"replyToken": replyToken, "messages" :[{"type": "text", "text" : msgText}, {"type": "image", "originalContentUrl": secure_url, "previewImageUrl": secure_url}]}
    else:
        contents = {"replyToken": replyToken, "messages" :[{"type": "text", "text" : msgText}]}

    res = requests.post(url, headers=headers, json=contents).json()

# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

