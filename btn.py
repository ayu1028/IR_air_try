from gpiozero import Button
from time import time, sleep
import subprocess

# button set on GPIO 27
button = Button(27, pull_up=False)

# power off command
args = ['sudo', 'poweroff']

try:
    while True:

        button.wait_for_press()
        press_time = time()  # 押された時刻を記録

        # ボタンが離されるまでループ
        while button.is_pressed:
            if time() - press_time >= 3:
                print('power off')
                subprocess.Popen(args)

                # print('hello!')

                # ボタンを離すまでの間に何度も表示されるのを防ぐ
                while button.is_pressed:
                    sleep(0.1)
                break
            sleep(0.1)

        # 離されたら、再び待機
        sleep(0.1)

except KeyboardInterrupt:
    pass

button.close()

