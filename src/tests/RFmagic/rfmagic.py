import sys
import argparse
import re
import time
import serial   # Install the pyserial module to get this

# Baud rate codes understood/returned by the APC220
BAUD_RATES = { 0: "1200", 1: "2400", 2: "4800", 3: "9600", 4: "19200", 5: "38400", 6: "57600" }



def Detect(ser):
    """
    Detection involves sending 0xAA 0xFF to the serial port while waiting for a response of
    0xA7. While detection is in progress, the EN pin on the APC220 (RTS on the UART) should
    alternate between high and low with a duty cycle of 0.326ms high/0.156ms low
    NB: Setting RTS to "True" makes it low; setting RTS to "False" makes it high
    """

    # Need three consecutive 0xA7 responses to our 0xAA in order to consider the radio present
    got=0
    rtsState=True
    ser.setRTS(rtsState)
    rtsStateChangeTime = 0
    while(True):
        if (time.time() >= rtsStateChangeTime):
            if (rtsState == True):
                rtsState = False
                rtsStateChangeTime = time.time()+0.326
            else:
                rtsState = True
                rtsStateChangeTime = time.time()+0.156
            ser.setRTS(rtsState)
        ser.write([ 0xAA, 0xFF ])
#        ser.flush()    # On Linux, this pauses for ~2ms which causes detection to fail
        r = ser.read()
        if (r and ord(r) == 0xA7):
            got = got + 1
        else:
            got = 0
        if (got == 3):
            ser.setRTS(False)
            return
        
    
def Read(ser, verbose, sendCmd=True):
    buf = []
    if (sendCmd): 
        # Write() calls this with sendCmd=False to read back the response
        print("Read():")
        ser.flushInput()
        ser.write([ 0xCC ])
    got=0
    while (got < 32):
        r = ser.read()
        if (len(r) == 1):
            if ((got == 0) and (ord(r) != 0x34)):
                # Expect first byte of response to be 0x34 (necessary to allow 0xA7s from detection to wash out)
                continue
#            print(hex(ord(r)))
            buf.append(ord(r))
            got = got + 1
    print("Frequency        = "+chr(48+(buf[0] & 0x0f))+chr(48+(buf[1] & 0x0f))+chr(48+(buf[2] & 0x0f))+"."+chr(48+(buf[3] & 0x0f))+chr(48+(buf[4] & 0x0f))+chr(48+(buf[5] & 0x0f)))
    print("Radio Baud Rate  = "+GetBaudRate(buf[6] & 0x0f))
    print("RF Power         = "+str(buf[7] & 0x0f))
    print("Serial Baud Rate = "+GetBaudRate(buf[8] & 0x0f))
    print("Serial Parity    = "+GetParity(buf[9] & 0x0f))
    if (verbose):
        print("Network ID       = 0x"+"{0:02x}{1:02x}".format(buf[12], buf[13]))
        print("Node ID          = 0x"+"{0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}".format(buf[14], buf[15], buf[16], buf[17], buf[18], buf[19]))
        print("Radio ID (fixed) = "+hex(buf[30]))
    

def Write(ser, verbose, frequency, power, serialbaud, radiobaud, parity):
    print("Write(): f="+frequency+"00MHz, radio baud="+radiobaud+", power="+str(power)+", serial baud="+serialbaud+", parity="+GetParity(parity))
    writebuf = [ 0xc3,                               # "Write" command
             0x34, 0x35, 0x30, 0x30, 0x30, 0x30,     # Frequency (KHz in ASCII)
             0x31,                                   # Radio baud rate (ASCII 0...4)
             0x39,                                   # RF power (ASCII 0...9)
             0x31,                                   # Serial baud rate (ASCII 0...6)
             0x30,                                   # Serial parity (ASCII 0=none, 1=odd, 2=even)
             0x00, 0x00,                             # Always 0
             0x00, 0x01,                             # Network ID
             0x12, 0x34, 0x56, 0x78, 0xab, 0xcd,     # Node ID
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00,     # Always 0
             0x00, 0x00, 0x00, 0x00,                 # Always 0
             0x00,                                   # Serial number of some kind? write=00
             0xd2 ]                                  # Always D2
    
    # Frequency
    writebuf[1] = ord(frequency[0])
    writebuf[2] = ord(frequency[1])
    writebuf[3] = ord(frequency[2])
    writebuf[4] = ord(frequency[4])  # Skipped decimal point
     
    # Radio baud rate
    writebuf[7] = GetBaudCode(radiobaud)
    
    # Power
    writebuf[8] = 0x30+power
    
    # Serial baud rate
    writebuf[9] = GetBaudCode(serialbaud)
    
    # Parity
    writebuf[10] = 0x30+parity
    
    # Write updated values to the radio
    ser.flushInput()
    ser.flushOutput()
    ser.write(writebuf)
    
	# Handle the 32-byte response to the Write command
    Read(ser, verbose, False)

    
    
def GetBaudRate(key):
    """
    Map the one-byte value understood by the APC220 radio (0...6) to a
    human-readable baud rate string
    """
    global BAUD_RATES
    return BAUD_RATES[key]
    
def GetBaudCode(rate):
    """
    Map a human-readable baud-rate string to the one-byte value understood 
    by the APC220 radio (0...6) 
    """
    global BAUD_RATES
    codes = { v: k for k, v in BAUD_RATES.items() }
    return codes[rate]
    
    
    
    
def GetParity(key):
    parities = { 0: "None", 1: "Odd", 2: "Even" }
    return parities[key]
    
    

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    read_parser = subparsers.add_parser("read", help="Read settings from APC220")
    read_parser.add_argument("-v", help="Verbose output (extra parameters)", action="store_const", const=True, default=False)
    read_parser.add_argument("readserialport", help="Serial port")

    write_parser = subparsers.add_parser("write", help="Write settings to APC220")
    #read_parser.add_argument("-v", dest="writeverbose", help="Verbose output (extra parameters)", action="store_const", const=True, default=False)
    write_parser.add_argument("writeserialport", help="Serial port")
    write_parser.add_argument("frequency", help="Frequency (NNN.N : 418.0 - 455.0 in 200KHz steps)")
    write_parser.add_argument("rfpower", help="RF power", type=int, choices=range(0, 10))
    write_parser.add_argument("baud", help="Baud rate (line and radio)", choices=["1200", "2400", "4800", "9600", "19200"])

    #parser.add_argument("serialport", help="Serial port")
    args = parser.parse_args()

    if ('readserialport' in args):
        action = "read"
        serialport = args.readserialport
        verbose = args.v
    elif ('writeserialport' in args):
        action = "write"
        verbose = False
        serialport = args.writeserialport

        # Validate frequency
        #m = re.match("^(4[12345][0-9])\.([02468])$",args.frequency)
        m = re.match(r"^(4[12345][0-9])\.\([02468])$", args.frequency)
        if (not m):
            parser.exit(status=-1, message="Invalid frequency. Frequency must be between 418.0Mhz and 455.0MHz and must be an even multiple of 200KHz\n")
        if (int(m.group(1))*1000+int(m.group(2))*100 > 455000):
            parser.exit(status=-1, message="Invalid frequency. Frequency must be between 418.0Mhz and 455.0MHz and must be an even multiple of 200KHz\n")
              
    try:
        ser = serial.Serial(port=serialport,baudrate="115200",timeout=0)
    except Exception as e:
        print(e)
        sys.exit(-1)
        
    #print("ser="+str(ser))

    Detect(ser)
    print("Detected APC220 radio.  Reading current settings...")
    Read(ser, verbose)
    if (action == "write"):
        Detect(ser)
        print("\nWriting new settings to radio...these are the values returned during the \"write\" process:")
        Write(ser, verbose, args.frequency, args.rfpower, args.baud, args.baud, 0)
        Detect(ser)
        print("\nReading (hopefully) updated settings from radio...")
        Read(ser, verbose)
    print("\ndone!")



if (__name__ == '__main__'):
    main()