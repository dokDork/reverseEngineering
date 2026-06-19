#!/usr/bin/env python3

import logging
from datetime import datetime
from boofuzz import *
from boofuzz.connections.tcp_socket_connection import TCPSocketConnection
from urllib.parse import quote


# =========================================================
# LOG FILE TIMESTAMP
# =========================================================
start_time = datetime.now().strftime("%Y%m%d-%H%M%S")
log_file = f"full_log_{start_time}.log"

current_test_case = None


# =========================================================
# CALLBACK: INIZIO TEST CASE (SCRIVE HEADER UNA VOLTA)
# =========================================================
def on_test_case_start(target, fuzz_data_logger, session, *args, **kwargs):
    global current_test_case

    current_test_case = session.mutant_index

    with open(log_file, "a") as f:
        f.write("\n")
        f.write(f"==============================\n")
        f.write(f"TEST CASE {current_test_case}\n")
        f.write(f"==============================\n")


# =========================================================
# PATCH SEND: COSTRUISCE HTTP POST CON USER/PASS
# =========================================================
original_send = TCPSocketConnection.send


def send_and_log(self, *args, **kwargs):
    data = kwargs.get("data")
    if data is None:
        data = args[0] if args else b""

    if isinstance(data, bytes):
        user_value = data.decode("utf-8", errors="replace")
    else:
        user_value = str(data)

    password = "TestPass123"
    body = f"username={quote(user_value)}&password={password}"
    http_request = (
        f"POST /login HTTP/1.1\r\n"
        f"Host: 192.168.1.111:8080\r\n"
        f"Content-Type: application/x-www-form-urlencoded\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"{body}"
    ).encode()

    with open(log_file, "a") as f:
        f.write(http_request.decode(errors="ignore"))
        f.write("\n")

    return original_send(self, http_request)


TCPSocketConnection.send = send_and_log


# =========================================================
# FUZZER
# =========================================================
def main():
    target_ip = "192.168.1.111"
    target_port = 8080

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    session = Session(
        target=Target(
            connection=TCPSocketConnection(target_ip, target_port)
        ),
        sleep_time=0.3,
        restart_interval=2,
        crash_threshold_request=1,
        crash_threshold_element=1,
        post_test_case_callbacks=[on_test_case_start],
    )

    # =========================================================
    # FUZZ DEL CAMPO USER (in HTTP POST)
    # =========================================================
    s_initialize("http_login_user_fuzz")
    s_string(
        "admin",
        fuzzable=True,
        name="user_field",
        max_len=10000,
    )

    # COLLEGA IL NODO ALLA SESSIONE
    session.connect(s_get("http_login_user_fuzz"))

    print("[*] Avvio fuzzing campo USER su HTTP POST login")
    print(f"[*] Target: {target_ip}:{target_port}/login.php")
    print(f"[*] Password fissa: TestPass123")
    print(f"[*] Log file: {log_file}")
    print("[*] Ctrl+C per fermare\n")

    # Passa il nome come STRINGA, non l'oggetto Request
    session.fuzz("http_login_user_fuzz")


if __name__ == "__main__":
    main()
