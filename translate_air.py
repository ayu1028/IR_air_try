import json

def find_single_index(array, target):
    for i, val in enumerate(array):
        if val == target:
            return i
    return None

with open("IR_data_air.json", "r") as f:
    signals = json.load(f)

signal_name = input("input signal name: ")

signal_bin = signals[signal_name]["bin"]

T = 425 # [us]

signal = []
for i in range(len(signal_bin)):
    if i == len(signal_bin)-1:
        signal.append(T)
        break

    elif signal_bin[i] == "header":
        signal.append(10000)
        signal.append(25000)

    elif signal_bin[i] == "leader":
        signal.append(T*8)
        signal.append(T*4)
    
    elif signal_bin[i] == "trailer":
        signal.append(T)
        signal.append(35000)

    elif signal_bin[i] == 1:
        signal.append(T)
        signal.append(T*3)

    else :
        signal.append(T)
        signal.append(T)

gap_index = find_single_index(signal, 35000)
frame1 = signal[0:gap_index]
frame2 = signal[gap_index+1:]
inputData = { f"{signal_name}_frame1": frame1, f"{signal_name}_frame2": frame2 }

with open(f"IR_data_{signal_name}.json", "w") as f:
    saveData = json.dumps(inputData, sort_keys=False).replace("},", "},\n")
    saveData = saveData.replace("],", "],\n")
    saveData = saveData.replace("{", "{\n")
    f.write(saveData + "\n")

