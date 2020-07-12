import serial
import binascii
import time

resp_len = 2405

### PROTOCOL DESCRIPTION

# if user wants to use following commands, they needs to be defined as byte array b'...', 
# where bytes in hexadecimal are specified with \x start
# default 0A password for 13.55 MHz tags - FF FF FF FF FF FF

### EXAMPLE
# AB BA 00 16 05 00 00 03 92 5D DF
# WHERE AB BA is always at the start
# following 00 is address
# 05 is data length in bytes 
# 00 00 03 92 5D is data with length 5
# DF is xor checksum for whole array except AB BA https://www.scadacore.com/tools/programming-calculators/online-checksum-calculator/

port = serial.Serial("/dev/tty.usbserial", baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)

prefix = bytearray.fromhex("AB BA")

read_uid = bytearray(b'\xab\xba\x00\x10\x00\x10')
write_uid = bytearray(b'\xab\xba\x00\x11\x04\xc9\xc7\xa3\xc1\x79')
#write_uid = bytearray(b'\xab\xba\x00\x11\x0c\x00\x0a\xff\xff\xff\xff\xff\xff\xc9\xc7\xa3\xc1\x7b')
change_pwd = bytearray(b'\xab\xba\x00\x14\x0e\x00\x0a\x01\x02\x03\x04\x05\x06\xff\xff\xff\xff\xff\xff\x17')
read_id = bytearray(b'\xab\xba\x00\x15\x00\x15')
write_id = bytearray(b'\xab\xba\x00\x16\x05\x00\x00\x03\x92\x5d\xdf')
read_all = bytearray(b'\xab\xba\x00\x17\x07\x0a\xff\xff\xff\xff\xff\xff\x1a')
read_ultracard_id = bytearray(b'\xab\xba\x00\x19\x00\x19')
read_tag_sector = bytearray(b'\xab\xba\x00\x20\x00\x20')
write_tag_sector = bytearray(b'\xab\xba\x00\x21\x05\x54\x00\x82\x10\x9e\x7c')

menu = {0:read_uid,1:write_uid,4:change_pwd,5:read_id,6:write_id,7:read_all,9:read_ultracard_id,10:read_tag_sector,11:write_tag_sector}

menustring = """
    0) 0x10 read UID number
    1) 0x11 write UID number "4 bytes", use the default window code fffffffffff
    2) 0x12 read specified sector
    3) 0x13 write specified sector
    4) 0x14 Change group A or group B password
    5) 0x15 Read ID card number
    6) 0x16 write T5577 card number
    7) 0x17 Read the data of all blocks in all local areas (M1-1K card)
    9) 0x19 Read tag card UID (Ultralight card)
    10) 0x20 read tag card sector
    11) 0x21 write tag card sector """

def readAll(rcv):
    text = binascii.hexlify(rcv)
    output = []
    pom = ""
    for i in range(len(text)):
        pom += text[i]
        if i%48 == 47:
            output.append(pom)
            pom = ""
    return output

def main():
    print(menustring)

    choice = input("Choose option from menu: ")


    if (choice == 4):
        # passwords have length 6 bytes each so total length with region 00 and 0a mark for password type makes 14 or 0e in hex
        print("Enter passwords in hex format with length exactly 6 bytes")
        old_pass = bytearray.fromhex(raw_input("Enter old password: "))
        new_pass = bytearray.fromhex(raw_input("Enter new password: "))
        command = bytearray.fromhex("00 14 0e 00 0a")
        command = command+old_pass+new_pass
        command = command+checksum(binascii.hexlify(command))
        command = prefix + command
        menu[4] = command

    while True:
        print("writing...")
        port.write(menu[choice])
        rcv = port.read(resp_len)

        if (choice == 7):
            text = readAll(rcv)
            for line in text:
                print(line)

        else:
            print(binascii.hexlify(rcv))
        time.sleep(2)

def checksum(inp):
    xor = 0
    input = [inp[i:i+2] for i in range(0, len(inp), 2)]
    for byte in input:
        xor ^= int(byte,16)
    return bytearray.fromhex(hex(xor)[2:])

if __name__ == "__main__":
    main()
