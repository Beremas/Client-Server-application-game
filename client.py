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

    class UserDetails:
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

        def get_gender(self):
            return self.gender

    def init_socket(self, args):
        self.startedat = get_date_and_hour()
        self.closedat = ""
        self.server_ip = args.ip
        self.server_port = int(args.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_user_interface(self):
        run_client()

    def close_socket(self):
        client.socket.close()

    def connect_to(self, ip, port):
        self.socket.connect((ip, port))

    def send_encoded_message_via_socket(self, message):
        client.socket.send(encode_utf_8(message))

    def read_decoded_message_via_socket(self):
        return decode_utf_8(client.socket.recv(1024))




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
    SAVE = "Save"
    BACK = "Back"


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


def reset_curses():
    # reverse everything that you changed about the terminal
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    # restore the terminal to its original state
    curses.endwin()

    return stdscr


def init_curses():
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


def send_nicer_good_bye():
    nice_good_bye_message = "CTRL+C"
    client.socket.send(encode_utf_8(nice_good_bye_message))
    client.close_socket()
    stdscr = reset_curses()


def sigint_handler(signum,frame):
    send_nicer_good_bye()
    exit(1)


"""EMBEDDED FUNCTIONS"""


def select_option(attributes, screen_options, screen_title, screen_marked_line):
    last_char_read = 0  # last character read
    #screen_marked_line = 0  # the current option that is marked
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

#TODO: NOT COMPLETED YET
def get_from_server_all_user_details():
    #client.UserDetails.username
    #client.UserDetails.username
    client.UserDetails.gender = ""
    client.UserDetails.age = ""
    client.UserDetails.email = ""


def profile_screen():

    login_color_attributes = init_curses_attributes()

    get_from_server_all_user_details()

    username = client.UserDetails.username
    password = client.UserDetails.password
    gender = client.UserDetails.gender
    age = client.UserDetails.age
    email = client.UserDetails.email

    screen_title = "Profile area"
    screen_options = ["Username(*) = " + username, "Password(*) = " + password, "Gender = " + gender, "Age = " + age, "Email(*) = " + email, "Save", "Back" ]


    loop_for_the_correct_details = True
    while loop_for_the_correct_details:

        screen_option_index = -1
        last_option_pressed = 0

        while screen_option_index != screen_options.index("Save") and screen_option_index != screen_options.index("Back"):
            screen_option_index = select_option(login_color_attributes, screen_options, screen_title, last_option_pressed)
            last_option_pressed = screen_option_index

            curses.echo()
            stdscr.keypad(False)
            curses.curs_set(2)

            if screen_option_index == screen_options.index(screen_options[0]):
                username = decode_utf_8(stdscr.getstr(2, 17, 30)).strip()
                screen_options[0] = "Username(*)" + " = " + username

            elif screen_option_index == screen_options.index(screen_options[1]):
                password = decode_utf_8(stdscr.getstr(3, 17, 30)).strip()
                screen_options[1] = "Password(*)" + " = " + password

            elif screen_option_index == screen_options.index(screen_options[2]):
                gender = decode_utf_8(stdscr.getstr(4, 12, 30)).strip()
                screen_options[2] = "Gender" + " = " + gender

            elif screen_option_index == screen_options.index(screen_options[3]):
                age = decode_utf_8(stdscr.getstr(5, 19, 30)).strip()
                screen_options[3] = "Age" + " = " + age

            elif screen_option_index == screen_options.index(screen_options[4]):
                email = decode_utf_8(stdscr.getstr(6, 14, 30)).strip()
                screen_options[4] = "Email(*)" + " = " + email

            curses.noecho()
            curses.curs_set(0)
            stdscr.keypad(True)

        if screen_option_index == screen_options.index("Save"):
            new_details = []
            new_details.append(username)
            new_details.append(password)
            new_details.append(gender)
            new_details.append(age)
            new_details.append(email)

            formatted_credentials = str(";".join(map(str, new_details)))

            message_for_the_server = UIText.SAVE.value + "-" + formatted_credentials

            client.send_encoded_message_via_socket(message_for_the_server)

            server_reply = client.read_decoded_message_via_socket()

            if server_reply == ServerResponseStatus.ACK.value:
                print_message_and_press_enter_to_continue("\nNew details saved.")
                loop_for_the_correct_details = False

            elif server_reply == ServerResponseStatus.EMAIL_OR_USER_ALREADY_EXISTS.value:
                print_message_and_press_enter_to_continue("\nThis username or email already exists.")
                loop_for_the_correct_details = True
            else:
                splitted_message = server_reply.split(";")
                if splitted_message[0] == ServerResponseStatus.WRONG_USER_DETAILS.value:
                    stdscr.addstr("\n\nServer response:")
                    if "0" in splitted_message[1]:
                        stdscr.addstr("\n - Username: No special chars or spaces are allowed")
                    if "1" in splitted_message[1]:
                        stdscr.addstr("\n - Password: No empty string allowed")
                    if "2" in splitted_message[1]:
                        stdscr.addstr("\n - Gender: can't contains special chars or digits")
                    if "3" in splitted_message[1]:
                        stdscr.addstr("\n - Age: digits only.")
                    if "4" in splitted_message[1]:
                        stdscr.addstr("\n - Email: wrong format. (i.e.: example@example2.com)")

                    print_message_and_press_enter_to_continue("\n\nPress ENTER..")
                    loop_for_the_correct_details = True

        elif screen_option_index == screen_options.index("Back"):

            message_for_the_server = UIText.BACK.value

            client.send_encoded_message_via_socket(message_for_the_server)

            server_reply = client.read_decoded_message_via_socket()

            if server_reply == ServerResponseStatus.ACK.value:
                loop_for_the_correct_details = False



    if screen_option_index == screen_options.index("Back"):
        no_need_to_disconnect = False
        return no_need_to_disconnect

    elif screen_option_index == screen_options.index("Save"):
        need_to_disconnect = True
        return need_to_disconnect


def home_screen():
    login_color_attributes = init_curses_attributes()

    screen_title = "Home screen. Player: " + client.UserDetails.username
    screen_options = [UIText.CONTINUE_GAME.value, UIText.PLAY_NEW_GAME.value, UIText.PLAY_COOP_GAME.value, UIText.PROFILE.value, UIText.LOGOUT.value]
    screen_option_index = -1
    last_option_pressed = 0

    while screen_option_index != screen_options.index(UIText.LOGOUT.value):
        screen_option_index = select_option(login_color_attributes, screen_options, screen_title, last_option_pressed)
        last_option_pressed = screen_option_index

        client.send_encoded_message_via_socket((screen_options[screen_option_index]))

        server_reply = client.read_decoded_message_via_socket()

        if server_reply == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.PLAY_NEW_GAME.value):

            print_message_and_press_enter_to_continue("Play new game - pressed\nPress ENTER to continue..")

        if server_reply == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.PLAY_COOP_GAME.value):

            print_message_and_press_enter_to_continue("Play coop game - pressed\nPress ENTER to continue..")

        if server_reply == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.CONTINUE_GAME.value):

            print_message_and_press_enter_to_continue("Continue game - pressed\nPress ENTER to continue..")

        if server_reply == ServerResponseStatus.ACK.value and screen_option_index == screen_options.index(UIText.PROFILE.value):

            need_disconnect_and_reconnect = profile_screen()
            if need_disconnect_and_reconnect:
                print_message_and_press_enter_to_continue("\nYou need to Sign in again in order to use use your changes. You will be redirected on the main screen.")
                screen_option_index = 4


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


def sign_in_screen():

    credentials = get_sign_in_details()

    client.send_encoded_message_via_socket(credentials)

    server_reply = client.read_decoded_message_via_socket()


    if server_reply == ServerResponseStatus.DENY.value:
        stdscr.addstr("\nWrong credentials!")
        print_message_and_press_enter_to_continue("\nPress ENTER..")
        return False

    if server_reply == ServerResponseStatus.USER_ALREADY_ONLINE.value:
        stdscr.addstr("\nThis user is already online!")
        print_message_and_press_enter_to_continue("\nPress ENTER..")
        return False

    if server_reply == ServerResponseStatus.ACK.value:
        stdscr.addstr("\nCredentials accepted!")
        print_message_and_press_enter_to_continue("\nPress ENTER..")

        splitted_credentials = credentials.split(";")
        client.UserDetails.username = splitted_credentials[0]
        client.UserDetails.password = splitted_credentials[1]
        return True


def sign_up_screen(server_reply):

    while server_reply != ServerResponseStatus.SIGNED.value:

        new_user_details = get_sign_up_details()

        client.send_encoded_message_via_socket(new_user_details)

        server_reply = client.read_decoded_message_via_socket()

        server_response_splitted = server_reply.split(";")

        if server_response_splitted[0] == ServerResponseStatus.WRONG_USER_DETAILS.value:
            stdscr.addstr("\n\nServer response:")
            if "0" in server_response_splitted[1]:
                stdscr.addstr("\n - Username: No special chars or spaces are allowed")
            if "1" in server_response_splitted[1]:
                stdscr.addstr("\n - Password: No empty string allowed")
            if "2" in server_response_splitted[1]:
                stdscr.addstr("\n - Gender: can't contains special chars or digits")
            if "3" in server_response_splitted[1]:
                stdscr.addstr("\n - Age: digits only.")
            if "4" in server_response_splitted[1]:
                stdscr.addstr("\n - Email: wrong format. (i.e.: example@example2.com)")

            print_message_and_press_enter_to_continue("\n\nPress ENTER..")

        elif server_reply == ServerResponseStatus.EMAIL_OR_USER_ALREADY_EXISTS.value:
            stdscr.addstr("\nUsername or email already exits.")
            print_message_and_press_enter_to_continue("\nPress ENTER to continue..")

        elif server_reply == ServerResponseStatus.SIGNED.value:
            stdscr.addstr("\nUser correctly registered!")
            print_message_and_press_enter_to_continue("\nPress ENTER to continue..")


def run_client():
    login_color_attributes = init_curses_attributes()

    screen_title = "Welcome traveler"
    screen_options_names = [UIText.SIGN_IN.value, UIText.SIGN_UP.value, UIText.EXIT.value]
    screen_option_index = -1
    last_option_pressed = 0

    while screen_option_index != screen_options_names.index(UIText.EXIT.value):

        screen_option_index = select_option(login_color_attributes, screen_options_names, screen_title, last_option_pressed)

        last_option_pressed = screen_option_index

        choice = screen_options_names[screen_option_index]

        client.send_encoded_message_via_socket(choice)

        server_reply = client.read_decoded_message_via_socket()


        if server_reply == ServerResponseStatus.ACK.value and screen_option_index == screen_options_names.index(UIText.SIGN_IN.value):
            if sign_in_screen():
                home_screen()

        elif server_reply == ServerResponseStatus.ACK.value and screen_option_index == screen_options_names.index(UIText.SIGN_UP.value):
            sign_up_screen(server_reply)

        elif server_reply == ServerResponseStatus.ACK.value and screen_option_index == screen_options_names.index(UIText.EXIT.value):
            pass



    return



# SIGNALS handler
signal.signal(signal.SIGINT, sigint_handler)

# ARGPARSE INIT
parser = argparse.ArgumentParser()
parser.add_argument("ip", help='type the server ip address')
parser.add_argument("port", help='type the server listening port ')
args = parser.parse_args()


try:

    stdscr = init_curses()

    client = Client()

    client.init_socket(args)

    client.connect_to(args.ip, int(args.port))

    client.start_user_interface()

    client.close_socket()

    stdscr = reset_curses()


except ConnectionRefusedError as cre:
    stdscr.addstr("Host unreachable.\n{}\n".format(cre))
    print_message_and_press_enter_to_continue("Press ENTER..")

except BrokenPipeError as bpe:
    os.system("clear")
    stdscr.addstr("Server is crashed. << {} >>\nConnection closed.\n".format(bpe))
    print_message_and_press_enter_to_continue("Press ENTER..")

except Exception as e:
    stdscr.addstr("Application aborted due to a fatal error.\n{}\n".format(e))
    print_message_and_press_enter_to_continue("Press ENTER..")

finally:
    client.close_socket()
    stdscr = reset_curses()