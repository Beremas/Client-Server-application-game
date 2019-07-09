#!/usr/bin/env python3
import argparse
import socket
import signal
import os
import curses
import threading
from enum import Enum
from datetime import datetime

"""CLASSES & ENUM"""


class Client:
    def __init__(self):
        self.server_ip = ""
        self.server_port = ""
        self.startedat = ""
        self.closedat = ""
        self.shutdown_time = ""
        self.socket = ""

    def start_socket(self, args):
        self.startedat = get_date_and_hour()
        self.closedat = ""
        self.server_ip = args.ip
        self.server_port = int(args.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def close_my_connection(self):
        client.socket.close()

    def connect_to_server(self, ip, port):
        self.socket.connect((ip, port))


class ProfileUser:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.gender = ""
        self.age = ""
        self.email = ""

    def reset_user(self):
        self.username = ""
        self.password = ""
        self.gender = ""
        self.age = ""
        self.email = ""


class GameStats:
    def __init__(self):
        self.username = ""
        self.life_points = ""
        self.kills = ""
        # [...]


class ServerResponseStatus(Enum):
    ACK = "Acknowledge"
    DENY = "Deny"
    WRONG_USER_DETAILS = "Wrong details"
    EMAIL_OR_USER_ALREADY_EXISTS = "Duplicate"
    SIGNED = "Signed up"
    USER_ALREADY_ONLINE = "User already online"


class UIText(Enum):
    PLAY_NEW_GAME = "Play new game"
    PLAY_COOP_GAME = "Play coop game"
    CONTINUE_GAME = "Continue game"
    PROFILE = "Profile"
    LOGOUT = "Logout"
    SIGN_IN = "Sign in"
    SIGN_UP = "Sign up"
    EXIT = "Exit"


"""UTILITY FUNCTIONS"""


def get_date_and_hour():
	return datetime.today().strftime('%d-%d-%Y %H-%M-%S')


def print_message_and_press_enter_to_continue(message):
    enter_pressed = False
    stdscr.addstr("{}".format(message))
    while enter_pressed is False:
        char = stdscr.getch()
        if char == 10:
            enter_pressed = True


def decode_utf_8(item):
    return item.decode('utf-8')


def encode_utf_8(item):
    return item.encode('utf-8')


"""CURSES FUNCTIONS"""


def reset_curses_options():
    # reverse everything that you changed about the terminal
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    # restore the terminal to its original state
    curses.endwin()

    return stdscr


def init_curses_options():
    # create a window object that represents the terminal window
    stdscr = curses.initscr()
    # Don't print what I type on the terminal
    curses.noecho()
    # React to every key press, not just when pressing "enter"
    curses.cbreak()
    # Enable easy key codes (will come back to this)
    stdscr.keypad(True)
    # Removue blinkin cursor
    curses.curs_set(0);
    init_curses_color_sets()

    return stdscr


def init_curses_color_sets():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)


def init_curses_attributes():
    attrib = {}
    attrib['normal'] = curses.color_pair(1)
    attrib['highlighted'] = curses.color_pair(2)

    return attrib


"""HANDLER FUNCTIONS"""


def sigint_handler(signum,frame):
    nice_good_bye_message = "CTRL+C"
    client.socket.send(encode_utf_8(nice_good_bye_message))
    client.close_my_connection()
    stdscr = reset_curses_options()

    exit(1)


"""EMBEDDED FUNCTIONS"""


def select_option(attributes, screen_options,screen_title):
    last_char_read = 0  # last character read
    screen_marked_line = 0  # the current option that is marked
    while last_char_read != 10:  # Enter in ascii
        stdscr.erase()
        stdscr.addstr("{}\n\n".format(screen_title), curses.A_UNDERLINE)
        for i in range(len(screen_options)):
            if i == screen_marked_line:
                attr = attributes['highlighted']
            else:
                attr = attributes['normal']
            stdscr.addstr("{0}. ".format(i + 1))
            stdscr.addstr(screen_options[i] + '\n', attr)
        last_char_read = stdscr.getch()
        if last_char_read == curses.KEY_UP and screen_marked_line > 0:
            screen_marked_line -= 1
        elif last_char_read == curses.KEY_DOWN and screen_marked_line < len(screen_options) - 1:
            screen_marked_line += 1

    return screen_marked_line


def load_user_profile(logged_user):
    logged_user_profile = {}
    # TODO: [...]

    return logged_user_profile


def run_user_logged_screen():
    login_color_attributes = init_curses_attributes()

    screen_title = "Hi " + logged_user.username
    screen_options = [UIText.PLAY_NEW_GAME.value, UIText.PLAY_COOP_GAME.value, UIText.CONTINUE_GAME.value, UIText.PROFILE.value, UIText.LOGOUT.value]
    screen_option_index = -1

    while screen_option_index != screen_options.index(UIText.LOGOUT.value):
        screen_option_index = select_option(login_color_attributes, screen_options, screen_title)

        client.socket.send(encode_utf_8(screen_options[screen_option_index]))

        server_reply = client.socket.recv(1024)

        if decode_utf_8(server_reply) == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.PLAY_NEW_GAME.value):

            print_message_and_press_enter_to_continue("Play new game - pressed\nPress ENTER to continue..")

        if decode_utf_8(server_reply) == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.PLAY_COOP_GAME.value):

            print_message_and_press_enter_to_continue("Play coop game - pressed\nPress ENTER to continue..")

        if decode_utf_8(server_reply) == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.CONTINUE_GAME.value):

            print_message_and_press_enter_to_continue("Continue game - pressed\nPress ENTER to continue..")

        if decode_utf_8(server_reply) == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.PROFILE.value):

            print_message_and_press_enter_to_continue("Profile - pressed\nPress ENTER to continue..")


        #TODO: [...]

    logged_user.reset_user()


def get_sign_up_details():
    credentials = []
    stdscr.erase()
    stdscr.addstr("Register your details here. Fields with (*) are necessaries.\n\n", curses.A_UNDERLINE)

    curses.echo()
    stdscr.keypad(False)
    curses.curs_set(2)

    stdscr.addstr("Username(*): \n")
    stdscr.addstr("Password(*): \n")
    stdscr.addstr("Gender: \n")
    stdscr.addstr("Age: \n")
    stdscr.addstr("Email(*): ")

    username = stdscr.getstr(2, 13, 30)
    password = stdscr.getstr(3, 13, 30)
    gender = stdscr.getstr(4, 8, 30)
    age = stdscr.getstr(5, 5, 30)
    email = stdscr.getstr(6, 10, 30)

    curses.noecho()
    curses.curs_set(0)
    stdscr.keypad(True)

    credentials.append(decode_utf_8(username))
    credentials.append(decode_utf_8(password))
    credentials.append(decode_utf_8(gender))
    credentials.append(decode_utf_8(age))
    credentials.append(decode_utf_8(email))

    formatted_credentials = str(";".join(map(str, credentials)))

    return formatted_credentials


def get_sign_in_details():
    userpasw = []
    stdscr.erase()
    stdscr.addstr("Insert your credentials\n\n", curses.A_UNDERLINE)

    curses.echo()
    curses.curs_set(2)
    stdscr.keypad(False)


    stdscr.addstr("Username: \n")
    stdscr.addstr("Password: ")

    username = stdscr.getstr(2, 10, 30)
    password = stdscr.getstr(3, 10, 30)

    curses.noecho()
    curses.curs_set(0)
    stdscr.keypad(True)

    userpasw.append(decode_utf_8(username))
    userpasw.append(decode_utf_8(password))

    credentials = str(";".join(map(str, userpasw)))

    return credentials


def run_sign_in_screen():
    credentials =get_sign_in_details()

    client.socket.send(encode_utf_8(credentials))

    server_reply = client.socket.recv(1024)

    if decode_utf_8(server_reply) == ServerResponseStatus.DENY.value:
        stdscr.addstr("\nWrong credentials!")
        print_message_and_press_enter_to_continue("\nPress ENTER..")

        return False

    if decode_utf_8(server_reply) == ServerResponseStatus.USER_ALREADY_ONLINE.value:
        stdscr.addstr("\nThis user is already online! This action will be logged.")
        print_message_and_press_enter_to_continue("\nPress ENTER..")

        return False

    if decode_utf_8(server_reply) == ServerResponseStatus.ACK.value:
        stdscr.addstr("\nCredentials accepted!")
        print_message_and_press_enter_to_continue("\nPress ENTER..")
        splitted_credentials = credentials.split(";")
        logged_user.username = splitted_credentials[0]

        return True


def run_sign_up_screen(server_reply):
    while decode_utf_8(server_reply) != ServerResponseStatus.SIGNED.value:

        new_user_details = get_sign_up_details()

        print_message_and_press_enter_to_continue("\nPress ENTER to send.")

        client.socket.send(encode_utf_8(new_user_details))

        server_reply = client.socket.recv(1024)

        server_response_splitted = decode_utf_8(server_reply).split(";")

        if server_response_splitted[0] == ServerResponseStatus.WRONG_USER_DETAILS.value:
            stdscr.addstr("\n\nServer response:")
            if "0" in server_response_splitted[1]:
                stdscr.addstr("\n - Username: No special chars or empty string allowed")
            if "1" in server_response_splitted[1]:
                stdscr.addstr("\n - Password: No empty string allowed")
            if "2" in server_response_splitted[1]:
                stdscr.addstr("\n - Gender: can't contains special chars or digits")
            if "3" in server_response_splitted[1]:
                stdscr.addstr("\n - Age: digits only.")
            if "4" in server_response_splitted[1]:
                stdscr.addstr("\n - Email: wrong format. (i.e.: example@example2.com)")

            print_message_and_press_enter_to_continue("\n\nPress ENTER..")

        elif decode_utf_8(server_reply) == ServerResponseStatus.EMAIL_OR_USER_ALREADY_EXISTS.value:
            stdscr.addstr("\nUsername or email already exits.")
            print_message_and_press_enter_to_continue("\nPress ENTER to continue..")


        elif decode_utf_8(server_reply) == ServerResponseStatus.SIGNED.value:
            stdscr.addstr("\nUser correctly registered!")
            print_message_and_press_enter_to_continue("\nPress ENTER to continue..")
            break


def run_client():
    login_color_attributes = init_curses_attributes()

    screen_title = "Welcome traveler"
    screen_options = [UIText.SIGN_IN.value, UIText.SIGN_UP.value, UIText.EXIT.value]
    screen_option_index = -1

    try:
        while screen_option_index != screen_options.index(UIText.EXIT.value):

            screen_option_index = select_option(login_color_attributes, screen_options, screen_title)
            choice = screen_options[screen_option_index]
            client.socket.send(encode_utf_8(choice))

            server_reply = client.socket.recv(1024)

            if decode_utf_8(server_reply) == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.SIGN_IN.value):
                server_response = run_sign_in_screen()
                if server_response:
                    run_user_logged_screen()

            elif decode_utf_8(server_reply) == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.SIGN_UP.value):
                run_sign_up_screen(server_reply)

            elif decode_utf_8(server_reply) == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.EXIT.value):
                pass

        return

    except BrokenPipeError as bpe:
        os.system("clear")
        stdscr.addstr("Server is crashed. << {} >>\nConnection closed.\n".format(bpe))
        print_message_and_press_enter_to_continue("Press ENTER..")

    finally:
        client.close_my_connection()
        reset_curses_options()


# SIGNALS handler
signal.signal(signal.SIGINT, sigint_handler)

# ARGPARSE INIT
parser = argparse.ArgumentParser()
parser.add_argument("ip", help='type the server ip address')
parser.add_argument("port", help='type the server listening port ')
args = parser.parse_args()


try:

    stdscr = init_curses_options()

    client = Client()
    client.start_socket(args)
    client.connect_to_server(args.ip, int(args.port))

    logged_user = ProfileUser()

    run_client()

    #TODO: [...]

    client.close_my_connection()
    stdscr = reset_curses_options()


except ConnectionRefusedError as cre:
    stdscr.addstr("Host unreachable.\n{}\n".format(cre))
    print_message_and_press_enter_to_continue("Press ENTER..")

except Exception as e:
    stdscr.addstr("Application aborted due to a fatal error.\n{}\n".format(e))
    print_message_and_press_enter_to_continue("Press ENTER..")

finally:
    client.close_my_connection()
    stdscr = reset_curses_options()