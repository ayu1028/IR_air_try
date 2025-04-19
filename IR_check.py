import time
from gpiozero import Button
import json

# obtain read pin number
pin = 5
# obtain wait interval (us)
wait = 4e4
# Baud [us]
T = 425

button = Button(pin)

def current():
    return time.time() * 1e6

def scanSignal():
    buffer = [0.0] * 1024
    current_time = 0.0
    current_state = 0
    last_state = 0
    offset = 0

    last_state = button.is_pressed

    print(f"Scanning start")

    while True:
        current_time = current()
        if offset and current_time > buffer[offset - 1] + wait:
            break

        current_state = button.is_pressed
        if current_state != last_state:
            buffer[offset] = current_time
            offset += 1
            last_state = current_state

    print("Scanning end")

    data = []
    for i in range(1, offset):
        data.append(int(buffer[i] - buffer[i - 1]))
    
    return data


# def compareSignal(signal1: list, signal2: list):
#     signal1Len, signal2Len = len(signal1), len(signal2)
#     if signal1Len != signal2Len:
#         print(f"signal1 length(len:{signal1Len}) and signal2 length(len:{signal2Len}) are not equal")
#         return signal1
    
#     data = []
#     for i in range(signal1Len):
#         data.append(int((signal1[i] + signal2[i])*0.5))

#     return data


def main():
    fileName = "IR_data_module_test.json"
    signalName = input('input signal name:')

    scanData = scanSignal()
    # scanData2 = scanSignal(2)

    # data = compareSignal(scanData1, scanData2)

    signalData = { signalName: scanData }

    try:
        with open(fileName, "r") as f:
            inputData = json.load(f)
    except FileNotFoundError:
        inputData = {}
    
    inputData.update(signalData)

    with open(fileName, "w") as f:
        f.write(json.dumps(inputData, sort_keys=True).replace("],", "],\n")+"\n")
    
    print("Output end")

    return 0

if __name__ == "__main__":
    main()
