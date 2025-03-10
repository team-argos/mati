import sys
import re
import argparse
from datetime import datetime
import signal
import serial   # Install the pyserial module to get this



def usage(msg=None):
    if (msg):
        print("ERROR: "+msg+"\n")
    print("""usage: python apc220monitor.py COMx SPEED output-file

"COMx" should be the COM port that the APC220 radio is connected to
(typically COM2, but check this in Device Manager to be sure).

"SPEED" is the baud rate.  It is typically 9600 unless you have set your
APC220 radio to something different.  Only 2400, 4800 and 9600 are allowed.

"output-file" is the name of the file to save output to.  You can specify
a value of "nul", "/dev/null" or "-" here if you don't want data saved
to a file.

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
    Monitor data from a serial port (an APC220 radio connected via a USB
    adapter). Displays the output to the console and optionally writes it
    to a file.
    """)
    parser.add_argument("comPort", help="\"COMx\" should be the COM port that the APC220 radio is connected to (typically COM2, but check this in Device Manager to be sure)")
    parser.add_argument("baudRate", choices=("2400", "4800", "9600", "19200", "38400"), help="\"SPEED\" is the baud rate. It is typically 9600 unless you have set your APC220 radio to something different.")
    parser.add_argument("outFile", default=None, help="\"output-file\" is the name of the file to save output to.  You can specify a value of \"nul\" here if you don't want data saved to a file.")

    args = parser.parse_args()

    if (sys.platform.startswith("win")):
        if (not re.match(r"^COM\d+$",args.comPort,re.IGNORECASE)):
            usage("Invalid value for COM port")
    elif (sys.platform.startswith("linux") or sys.platform.startswith("darwin")):
        if (not re.match(r"^/dev/tty.+",args.comPort,re.IGNORECASE)):
            usage("Invalid value for COM port")

    f = None
    if (args.outFile and (args.outFile.lower() != "nul") and (args.outFile != "/dev/null") and (args.outFile != "-")):
        f = open(args.outFile, "a")
        f.write("="*80+"\n")
        f.write("Logging started at "+str(datetime.now())+"\n")
        f.write("="*80+"\n")
        print("Logging received data to "+args.outFile)

    ser = serial.Serial(port=args.comPort,baudrate=args.baudRate,timeout=0.5)
    ser.setRTS(False)
    while(True):
        try:
            b = ser.read()
            if (b):
                sys.stdout.write(b.decode(encoding="ascii", errors="replace"))
                sys.stdout.flush()
                if (f):
                    f.write(b.decode(encoding="ascii", errors="replace"))
                    if ((b == '\r') or (b == '\n')):
                        f.flush()	# Make sure it is flushed out to disk
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            sys.exit(0)



if (__name__ == '__main__'):
    main()