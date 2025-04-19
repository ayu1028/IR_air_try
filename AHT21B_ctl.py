from smbus2 import SMBus, i2c_msg
from time import sleep

bus = SMBus(1)

# ADT21B configurations
addr = 0x38
status_addr = 0x71
measure_trg = 0xAC

def sleep_ms(ms):
    sleep(ms/1000)

def read_status():
    write_message = i2c_msg.write(addr, [0x71])
    read_message = i2c_msg.read(addr, 1)

    bus.i2c_rdwr(write_message)
    bus.i2c_rdwr(read_message)

    return list(read_message)

def trigger_measurement():
    write_message = i2c_msg.write(addr, [0xAC, 0x33, 0x00])
    bus.i2c_rdwr(write_message)


def get_results(bytes: int):
    read_message = i2c_msg.read(addr, bytes)
    bus.i2c_rdwr(read_message)

    return list(read_message)

def read_ct_data():
    trigger_measurement()
    sleep_ms(80)

    cnt = 0
    while (read_status()[0] & 0x80) == 0x80:
        sleep_ms(80)
        cnt += 1
        if cnt >= 10:
            break
    
    data = get_results(6)

    hum = ((data[1]<<16) | (data[2]<<8) | data[3])>>4
    temp = ((data[3]<<16) | (data[4]<<8) | data[5]) & 0xFFFFF

    return hum, temp


# CRC check function
def calc_crc8(message: list, num: int) -> int:
    crc = 0xFF
    for byte_index in range(num):
        crc ^= message[byte_index]
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x31
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

# Initialize ADT21B if status is not equal to 0x18
def initialize():
    print('test')

# Main proccess
def main():
    sleep_ms(500)
    status = read_status()

    print(bin(status[0]))

    if read_status()[0] & 0x18 != 0x18:
        initialize()
        sleep_ms(10)
    try:
        while True:
            hum, temp = read_ct_data()
            
            hum = hum*100/1024/1024
            temp = temp*200/1024/1024-50

            print(f"RH: {int(hum)} %, T: {round(temp, 1)} degC")

            sleep(1)

    except KeyboardInterrupt:
        pass

    bus.close()

if __name__ == "__main__":
    main()
