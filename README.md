# 7941W RFID Reader/Writer tool

## Introduction
7941W is dual frequency (13.56 MHz, 125 KHz ) RFID reader and writer. It can read a variety of IC and ID cards (Mifare1K, UID card, IC card,T5577 ID card ...).

## Connection
7941W Reader/Writer contains 5 pins,
- **red** -> 5V pin
- **black** -> GND pin
- **green** -> RX recieve pin (when connecting to your PC, don't forget to connect to RX pin)
- **white** -> TX transmit pin (when connecting to your PC, connect to TX pin)
- **blue** -> (no information found)

For developing purposes, we used USB to UART cable and Mac OS powered computer.

## Protocol

This section's goal is not to give detailed technical information about the protocol, this can be found [here](http://www.icstation.com/dual-frequency-rfid-reader-writer-wireless-module-uart-1356mhz-125khz-icidmifare-card-p-12444.html). In the next lines, we want to focus on practical usage of this protocol and explain how it works the easy way.

### How to send/recieve data to/from Reader/Writer

Before explaining usage of the protocol itself, we need to find out how to send the information. Reader/Writer is connected to your PC as a Serial Device that can transmit (TX pin) and recieve (RX pin) information so it uses both way communication. 

#### Find the device name
When connecting the USB to UART cable, we can find out the device name by typing `ls /dev/tty*` into Mac OS terminal (linux systems can follow similar process). This command will list all devices starting with **tty** and we want to find the name containing words like `UART,usbserial` or something similar. Once we have our device name (in our case `/dev/tty.usbserial`), we can replace the first argument for `serial.Serial` object in `reader.py` code.

#### Protocol
Communication with device is based on sending and recieving bytes in the way defined by protocol. Python contains bytearray object which is suitable for this purpose and used in our tool. Bytes are written with starting `\x` followed by byte itself (e.g. f1 -> `\xf1`)

Now let's explain what these letters and numbers mean:

1. Reading ID from 13.56 MHz cards/keys - First and easiest message is reading command sent to Reader. This is the message:
```
ab ba 00 10 00 10
``` 
- first 2 bytes (or 4 signs) `AB BA` are prefix always used when defining commands. Following `00` is address where something will be read/written, in this case we use starting address. Next two bytes `10` define what command will be used (10 is code for reading from 13.56 MHz cards/keys). Following `00` is length (in bytes) of sent data. When reading, this is ofc length 0. The last part of the message is xor checksum. This can be calculated using [calculator](https://www.scadacore.com/tools/programming-calculators/online-checksum-calculator/) where you enter previous bytes except the starting `AB BA`, in our case `00 10 00`. There is also calculation for this in the code but not yet implemented for every function.

2. Writing new ID to 13.56 MHz cards/Keys
```
ab ba 00 11 04 c9 c7 a3 c1 79
```
Description
- `ab ba` prefix
- `00` address for writing (in case of id it is the starting address)
- `11` instruction code for writing ID to 13.56 MHz cards
- `04` length of data to be written
- `c9 c7 a3 c1` ID to be written
- `79` checksum

Note: Writing to card/key is possible only for specific writable cards/keys, similar for writing to 125 KHz keys/cards with instruction code `16`

Other instructions are still WIP...