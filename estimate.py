import json

def estimate_cb_count(pulse_us_list):
    cb_count = 0
    carrier_on = True
    for duration in pulse_us_list:
        if carrier_on:
            cycles = duration / 26.3  # 38kHz周期
            cb_count += int(cycles) * 2  # ON + OFF for each cycle
        else:
            cb_count += 1  # idle pulse
        carrier_on = not carrier_on
    return cb_count


with open("IR_data_air.json", "r") as f:
    signals = json.load(f)

signal = signals[input("input signal name: ")]["signal"]

cb_total = estimate_cb_count(signal)
print("estimated signal1 CB number:", cb_total)

