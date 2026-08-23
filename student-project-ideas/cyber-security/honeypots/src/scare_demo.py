#!/usr/bin/env python3
# scare_demo.py — run ONLY against your own honeypot / hosts you control
import argparse
import socket

payload = (
    b"\033[2J\033[H"                 # clear screen, cursor home
    b"\033[?25l"                     # hide cursor
    b"\033[41m\033[1;37m"            # white bold on red background
    b"\r\n\r\n"
    b"  ############################################################\r\n"
    b"  #                                                          #\r\n"
    b"  #                 !! SYSTEM COMPROMISED !!                 #\r\n"
    b"  #                                                          #\r\n"
    b"  #            All logs have been deleted.                   #\r\n"
    b"  #       root access obtained. Have a nice day.             #\r\n"
    b"  #                                                          #\r\n"
    b"  ############################################################\r\n"
    b"\033[0m\r\n"                    # reset colours
)


def main():
    parser = argparse.ArgumentParser(
        description="Send a fake scare banner to a honeypot you control."
    )
    parser.add_argument("host", help="target IP or hostname")
    parser.add_argument("port", type=int, help="target TCP port")
    parser.add_argument(
        "-t", "--timeout", type=float, default=5.0,
        help="connection timeout in seconds (default: 5)"
    )
    args = parser.parse_args()

    with socket.create_connection((args.host, args.port), timeout=args.timeout) as s:
        s.recv(1024)          # consume the fake banner
        s.sendall(payload)


if __name__ == "__main__":
    main()
