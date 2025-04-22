from smbus2 import SMBus, i2c_msg
from time import sleep
import sys

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

# LCD configurations
address_st7032 = 0x3e
register_setting = 0x00
register_display = 0x40

contrast = 32 # 0から63のコントラスト。30から40程度を推奨
chars_per_line = 8  # LCDの横方向の文字数
display_lines = 2   # LCDの行数

display_chars = chars_per_line*display_lines

def setup_st7032():
    trials = 5
    for i in range(trials):
        try:
            c_lower = (contrast & 0xf)
            c_upper = (contrast & 0x30)>>4
            bus.write_i2c_block_data(address_st7032, register_setting, [0x38, 0x39, 0x14, 0x70|c_lower, 0x54|c_upper, 0x6c])
            sleep(0.2)
            bus.write_i2c_block_data(address_st7032, register_setting, [0x38, 0x0d, 0x01])
            sleep(0.001)
            break
        except IOError:
            if i==trials-1:
                sys.exit()

def clear():
    bus.write_byte_data(address_st7032, register_setting, 0x01)
    sleep(0.001)

def check_writable(c):
    if c >= 0x06 and c <= 0xff :
        return c
    else:
        return 0x20 # 空白文字

def write_string(s):
    for c in list(s):
        byte_data = check_writable(ord(c))
        bus.write_byte_data(address_st7032, register_display, byte_data)

def new_line():
    bus.write_byte_data(address_st7032, register_setting, 0xc0)


# Main proccess
def main():
    # setup AHT21B
    sleep_ms(500)
    status = read_status()

    # print(bin(status[0]))

    if read_status()[0] & 0x18 != 0x18:
        initialize()
        sleep_ms(10)

    #setup LCD
    setup_st7032()

    try:
        while True:
            # measure temperature and humidity
            hum, temp = read_ct_data()
            
            hum = hum*100/1024/1024
            temp = temp*200/1024/1024-50

            # translate measurement results to LCD characters
            hum_char = "RH:" + str(int(hum)) + "%"
            temp_char = "T:" + str(round(temp, 1)) + chr(0xdf) + "C"

            # display characters on LCD
            clear()
            write_string(temp_char)
            new_line()
            write_string(hum_char)

            # print(f"RH: {int(hum)} %, T: {round(temp, 1)} degC")

            sleep(2)

    except KeyboardInterrupt:
        pass

    bus.close()

if __name__ == "__main__":
    main()
