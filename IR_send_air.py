import time
import json
import os
import pigpio

def carrier(gpio, frequency, micros):
    """
    Generate carrier square wave.
    """
    wf = []
    cycle = 1000.0 / frequency
    cycles = int(round(micros/cycle))
    on = int(round(cycle / 2.0))
    sofar = 0
    for c in range(cycles):
        target = int(round((c+1)*cycle))
        sofar += on
        off = target - sofar
        sofar += off
        wf.append(pigpio.pulse(1<<gpio, 0, on))
        wf.append(pigpio.pulse(0, 1<<gpio, off))
    return wf


pi = pigpio.pi()

# FILE = "IR_data_air.json"
# FILE = "IR_data_reibo_on_260.json"
FILE = "IR_data_air_test.json"
GPIO = 26
FREQ = 38.0 # [kHz], sub-carrier
GAP_S = 25/1000 # [s], gap between each wave (35ms)
# GAP_S = 0.0

if not pi.connected:
    exit(0)

try:
    f = open(FILE, "r")
except:
    print(f"Can't open: {FILE}")
    exit(0)

records = json.load(f)

f.close()

pi.set_mode(GPIO, pigpio.OUTPUT) # IR TX connected to this GPIO.

pi.wave_add_new()

emit_time = time.time()

# signals =[ "danbo_on_220_1", "danbo_on_220_2" ]
signals =[ "reibo_on_260_1", "reibo_on_260_2" ]

for arg in signals:
    if arg in records:

        # code = records[arg]["signal"]
        code = records[arg]

        # Create wave

        marks_wid = {}
        spaces_wid = {}

        wave = [0]*len(code)

        pi.wave_clear()
        for i in range(0, len(code)):
            ci = code[i]
            if i & 1: # Space
                if ci not in spaces_wid:
                    pi.wave_add_generic([pigpio.pulse(0, 0, ci)])
                    spaces_wid[ci] = pi.wave_create()
                wave[i] = spaces_wid[ci]
            else: # Mark
                if ci not in marks_wid:
                    wf = carrier(GPIO, FREQ, ci)
                    pi.wave_add_generic(wf)
                    marks_wid[ci] = pi.wave_create()
                wave[i] = marks_wid[ci]

        delay = emit_time - time.time()

        if delay > 0.0:
            time.sleep(delay)

        pi.wave_chain(wave)

        while pi.wave_tx_busy():
            time.sleep(0.001)
        
        emit_time = time.time() + GAP_S

        for i in marks_wid:
            pi.wave_delete(marks_wid[i])

        marks_wid = {}

        for i in spaces_wid:
            pi.wave_delete(spaces_wid[i])
        
        spaces_wid = {}
    else:
        print(f"Id {arg} not found")

pi.stop()
