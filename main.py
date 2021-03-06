import socket
import sys
import ipaddress
import argparse
import string
import random
import hashlib
import publicip
from simplecrypt import encrypt, decrypt

# My attempt at non-urine coding.

parser = argparse.ArgumentParser(description='Download Or Host Files over the Internet.')
# Default Message
parser.add_argument('-host', help='Host a file from this PC', action='store_true')
parser.add_argument('file', help='The file to send or receive into, depending on the mode.')
# HOST MODE
parser.add_argument('-client', help='Download a file from another PC.', action='store_true')
parser.add_argument('-ip', help='Remote PC IP', required='-client' in sys.argv)
parser.add_argument('-password', help='Connection Password', required='-client' in sys.argv)
# CLIENT MODE
parser.add_argument('-port', help='Remote or local port.', type=int, default=50000)
# GLOBAL ARG

args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])


if args.host:
    # HOST MODE
    hash = hashlib.sha512()
    letters = string.ascii_letters
    random_pass = (''.join(random.choice(letters) for i in range(11)))
    hashed_random = random_pass.encode('utf-8')
    hash.update(hashed_random)
    hex_dig = hash.digest()

    # generate random authentication password (not very hard but sufficient lol)
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        with open(args.file, 'rb') as file:
            sending = file.read()
            cipherfile = encrypt(hashed_random, sending)
            # Open the file in binary mode
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("Attempting to bind to socket...")
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            s.bind(('', args.port))
            s.listen(1)

            print("Socket Bind Success! Now attempting to open ports...")
            print("Details:\n", "Local Host: ", ip_address, "\nPort: ", args.port, "Password: ", random_pass)
            print("Public IP: ")
            publicip.get()  # why can't this module just work in a variable?????
            print("Waiting for connections...")
            while True:
                c, addr = s.accept()
                print("Got connection from", addr)
                pass_recv = c.recv(4096)
                stringdata = pass_recv

                if stringdata == hex_dig:
                    print("Pass Accepted.")
                    print("Sending.....")

                    c.send(cipherfile)
                    print("Send Completed!")
                    c.shutdown(socket.SHUT_RDWR)
                    c.close()
                    file.close()
                    sys.exit(0)
                else:
                    c.shutdown(socket.SHUT_RDWR)
                    c.close()
                    file.close()
                    print("Client pass failed!")

        except socket.error:
            print("Socket bind failed!")
            sys.exit(1)

        except KeyboardInterrupt:
            sys.exit(0)

    except FileNotFoundError:
        print("File not Found!")
    except OverflowError:
        print("Port must be 1-65535!")
    except IsADirectoryError:
        print("Attempted to host a directory!")

if args.client:
    # CLIENT MODE
    try:
        ipaddress.ip_address(args.ip)
        print("Creating Socket")
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((args.ip, args.port))
        print("Creating Socket Success!")
        hash = hashlib.sha512()
        drypass = args.password
        encoded = drypass.encode('utf-8')
        hash.update(encoded)
        hex_dig = hash.digest()
        conn.send(hash.digest())
        msg = b""
        with open(args.file, 'wb') as f:
            print("Created New File!")
            print('Receiving Data...')
            while True:
                data = conn.recv(8192)

                msg += data

                if not data:
                    break

            decrypted = decrypt(encoded, msg)
            f.write(decrypted)
            f.close()

            print("Complete.")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            sys.exit(0)

    except ValueError:
        print("Invalid IP!")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
    except BrokenPipeError:
        print("Remote host disconnected!")
        conn.close()
    except TimeoutError:
        print("Connection Attempt Timed out!")
        conn.close()
    except ConnectionRefusedError:
        print("Host is not receiving!")
        conn.close()







