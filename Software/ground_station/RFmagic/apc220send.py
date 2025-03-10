import sys
import re
import argparse
from datetime import datetime
import signal
import serial   # Install the pyserial module to get this
from time import sleep



def usage(msg=None):
    if (msg):
        print("ERROR: "+msg+"\n")
    print("""usage: python apc220send.py COMx SPEED

"COMx" should be the COM port that the APC220 radio is connected to
(typically COM2, but check this in Device Manager to be sure).

"SPEED" is the baud rate.  It is typically 9600 unless you have set your
APC220 radio to something different.  Only 2400, 4800 and 9600 are allowed.

The message to send is read from standard input
""")
    sys.exit(-1)



def signal_handler(signal, frame):
        print("Bye!")
        sys.exit(0)



def main():
    # Set up signal-handler so that the script can be exitted easily
    signal.signal(signal.SIGINT, signal_handler)

    # Check command-line arguments
    parser = argparse.ArgumentParser(
        description = """\
    Read data from standard input and transmit it via an APC220 radio
    connected to the specified serial port.
    """)
    parser.add_argument("-v", "--verbose", action="store_true", help="Produce verbose output", default=False)
    parser.add_argument("comPort", help="\"COMx\" should be the COM port that the APC220 radio is connected to (typically COM2, but check this in Device Manager to be sure)")
    parser.add_argument("baudRate", choices=("2400", "4800", "9600", "19200", "38400"), help="\"SPEED\" is the baud rate. It is typically 9600 unless you have set your APC220 radio to something different.")

    args = parser.parse_args()

    if (sys.platform.startswith("win")):
        if (not re.match(r"^COM\d+$",args.comPort,re.IGNORECASE)):
            usage("Invalid value for COM port")
    elif (sys.platform.startswith("linux") or sys.platform.startswith("darwin")):
        if (not re.match(r"^/dev/tty.+",args.comPort,re.IGNORECASE)):
            usage("Invalid value for COM port")

    ser = serial.Serial(port=args.comPort, baudrate=args.baudRate)
    ser.setRTS(False)

    sleep(0.1)
    #print(sys.stdin.read().encode(encoding="ascii", errors="replace"))
    sent = 0
    if (sys.stdin.isatty()):
        # Interacive-mode: read and send one line at a time
        print("Reading from standard input: ", end="")
        if (sys.platform.startswith("win")):
            print("end with CTRL-Z on a line on its own")
        elif (sys.platform.startswith("linux") or sys.platform.startswith("darwin")):
            print("end with CTRL-D on a line on its own")
        while(True):
            buf = sys.stdin.readline()
            if (buf):
                n = ser.write(buf.encode(encoding="ascii", errors="replace"))
                sent += n
                ser.flush()
                if (args.verbose):
                    print(f"Sent {n} characters ({sent} in total)")
            else:
                break
    else:
        sent = ser.write(sys.stdin.read().encode(encoding="ascii", errors="replace")) 
        ser.flush()
        print(f"Sent {sent} bytes. Pausing for 5 seconds to ensure output buffers flushed.")
        sleep(5)		# ser.flush() is supposed to wait until everything is sent, but it doesn't seem to :-(
    ser.close()
    print("Bye!")


if (__name__ == '__main__'):
    main()