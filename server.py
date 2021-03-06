#!/usr/bin/env python3
import json
import argparse
import socket
import errno
import signal
import threading
from threading import Lock
import os
from datetime import datetime
import curses
from enum import Enum
import re

"""CLASSES & ENUM"""


class Server:
	def __init__(self):
		self.ip = ""
		self.port = ""
		self.startedat = ""
		self.closedat = ""
		self.shutdown_time = ""
		self.socket = ""
		self.status = ""
		self.RUNNING = ""

		self.list_of_connection_details = []
		self.list_of_online_users = []
		self.list_of_logs = []

	def init_socket(self, args):
		self.startedat = get_date_and_hour()
		self.closedat = ""
		self.ip = args.ip
		self.port = int(args.port)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((server.ip, server.port))
		self.socket.listen(MAXIMUM_CLIENTS_CONNECTIONS)
		self.status = "ON"

	def close_client_connection(self, client_socket):
		client_socket.close()

	def close_scoket(self):
		self.socket.close()

	def print_init_stats(self):
		print("Server specs:\n	ip: {}\n	port: {}\n	started at: {}\nServer status: {}".format(server.ip, server.port, server.startedat, server.status))

	def print_closing_stats(self):
		os.system("clear")
		self.closedat = get_date_and_hour()
		self.status = "OFF"
		print("Server specs:\n	ip: {}\n	port: {}\n	closed at: {}\nServer status: {}".format(server.ip, server.port, server.closedat, server.status))

	def print_executable_commands(self):
		print("Server executable <debug> commands: [online users, online connections, show/export logs, clear, clear logs]\n")

	def print_online_connections(self):
		if self.list_of_connection_details:
			print("List of accepted connections:")
			for connection in self.list_of_connection_details:
				thread = connection.get("THREAD")
				clientSocket = connection.get("CLIENT SOCKET")
				address = connection.get("ADDRESS")
				print("Thread info: {}\nClient Socket info: {}\nAddress info: {}\n".format(thread, clientSocket, address))
		else:
			print("List of accepted connections: empty")

	def print_list_of_logs(self):
		if self.list_of_logs:
			print("List of logs:")
			for logs in self.list_of_logs:
				print("	"+logs)
		else:
			print("List of logs: empty")

	def print_online_users(self):
		if self.list_of_online_users:
			print("List of online user(s): {}".format(len(self.list_of_online_users)))
			for index, user in enumerate(self.list_of_online_users):
				print("	User {}: {}".format(index+1, user))
		else:
			print("List of online user(s): empty")

	def clear_list_of_logs(self):
		self.list_of_logs = []

	# thread safe
	def remove_connection(self, param_ip, param_port):
		lock = Lock()
		lock.acquire()

		for currAddress in self.list_of_connection_details:
			add = currAddress.get("ADDRESS")
			curr_ip = add[0]
			curr_port = add[1]
			if param_ip == curr_ip and curr_port == param_port:
				self.list_of_connection_details.remove(currAddress)
				continue

		lock.release()

	# thread safe
	def add_connection(self, user_handler_thread, client_socket, address):
		lock = Lock()
		lock.acquire()

		dictionary_connection_details = { "THREAD": user_handler_thread, "CLIENT SOCKET": client_socket, "ADDRESS": address }
		self.list_of_connection_details.append(dictionary_connection_details)

		lock.release()

	# thread safe
	def add_user_to_online_list(self, username):
		lock = Lock()
		lock.acquire()
		if username not in self.list_of_online_users:
			self.list_of_online_users.append(username)
		lock.release()

	# thread safe
	def remove_user_from_online_list(self, username):
		lock = Lock()
		lock.acquire()
		for online_user in self.list_of_online_users:
			if online_user == username:
				self.list_of_online_users.remove(online_user)
		lock.release()

	# thread safe
	def save_existing_user_new_credentials(self, new_details, old_username):
		lock = Lock()
		lock.acquire()

		temporary_user_list_from_json = []

		if os.path.exists('usersDB.json'):
			with open('usersDB.json') as json_file:
				temporary_user_list_from_json = json.load(json_file)

				for user in temporary_user_list_from_json:
					curr_username = user.get("username")
					if curr_username == old_username:
						temporary_user_list_from_json.remove(user)
						break

				temporary_user_list_from_json.append(new_details)

				with open('usersDB.json', 'w')as json_file:
					json.dump(temporary_user_list_from_json, json_file)
				temporary_user_list_from_json = []
		else:
			temporary_user_list_from_json.append(new_details)
			with open('usersDB.json', 'w') as json_file:
				json.dump(temporary_user_list_from_json, json_file)
			temporary_user_list_from_json = []

		lock.release()

	# thread safe
	def save_user_credentials(self, user):
		lock = Lock()
		lock.acquire()

		temporary_user_list_from_json = []

		if os.path.exists('usersDB.json'):
			with open('usersDB.json') as json_file:
				temporary_user_list_from_json = json.load(json_file)

				temporary_user_list_from_json.append(user)

				with open('usersDB.json', 'w')as json_file:
					json.dump(temporary_user_list_from_json, json_file)
				temporary_user_list_from_json = []
		else:
			temporary_user_list_from_json.append(user)
			with open('usersDB.json', 'w') as json_file:
				json.dump(temporary_user_list_from_json, json_file)
			temporary_user_list_from_json = []

		lock.release()

	# thread safe
	def is_user_online(self, username):
		lock = Lock()
		lock.acquire()

		user_online = False
		for online_user in self.list_of_online_users:
			if online_user == username:
				user_online = True
		return user_online

		lock.release()

	# thread safe
	def validate_user(self, username, password):
		lock = Lock()
		lock.acquire()
		if not os.path.exists('usersDB.json'):
			return False
		else:
			with open('usersDB.json') as json_file:
				data = json.load(json_file)
				userfound = False
				for json_user in data:
					json_username = json_user["username"]
					json_password = json_user["password"]

					if username == json_username and password == json_password:
						userfound = True
						break
			return userfound

		lock.release()

	# thread safe
	def is_already_signed(self, username, email):
		lock = Lock()
		lock.acquire()
		if not os.path.exists('usersDB.json'):
			return False
		else:
			with open('usersDB.json') as json_file:
				data = json.load(json_file)
				userfound = False
				for json_user in data:
					json_username = json_user["username"]
					json_email = json_user["email"]

					if username == json_username or email == json_email:
						userfound = True
						break
			return userfound

		lock.release()

	def close_all_connections(self):
		for connection in self.list_of_connection_details:
			clientSocketExcracted = connection.get("CLIENT SOCKET")
			clientSocketExcracted.close()

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


def write_on_file(filename, items):
	with open(filename, 'w') as f:
		for item in items:
			f.write("%s\n" % item)


def is_valid_email(email):
	standard_pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"
	pattern = re.compile(standard_pattern)
	if not re.match(pattern, email):
		return False
	elif not standard_pattern:
		return False
	else:
		return True


def is_valid_format(username):
	specialc = " !#$%&'()*+,-./:;<=>?@[\]^_`{|}~\""

	for specC in specialc:
		if specC in username:
			return True
	return False


def decode_utf_8(item):
	return item.decode('utf-8')


def encode_utf_8(item):
	return item.encode('utf-8')


"""HANDLER FUNCTIONS"""

def close_server():
	server.RUNNING = False
	server.close_all_connections()
	server.print_closing_stats()
	server.close_scoket()

def sigint_handler(signum, frame):
	close_server()
	exit(1)


"""EMBEDDED FUNCTIONS"""


def is_the_reply_ctrlc(client_reply):
	return True if client_reply == "CTRL+C" else False


def is_the_reply_exit(client_reply):
	return True if client_reply == UIText.EXIT.value else False


def handle_profile_screen(client_reply, client_socket, address, username_logged):
	ack = ServerResponseStatus.ACK.value
	client_socket.send(encode_utf_8(ack))
	server.list_of_logs.append("	({}) {}:{} <-- ACK {}.".format(get_date_and_hour(), address[0], address[1], client_reply))

	need_to_disconnect_the_client = False
	client_is_crashed = False
	profile_loop = True

	while profile_loop is True:

		client_reply = decode_utf_8(client_socket.recv(1024))
		client_reply_splitted = client_reply.split("-")

		if is_the_reply_ctrlc(client_reply_splitted):
			server.list_of_logs.append("	({}) {}:{} --> CRASHED.".format(get_date_and_hour(), address[0], address[1] ))
			server.remove_connection(address[0], address[1])
			profile_loop = False
			client_is_crashed = True

		elif client_reply_splitted[0] == UIText.SAVE.value:

			splitted_details = client_reply_splitted[1].split(";")

			username = splitted_details[0]
			password = splitted_details[1]
			gender = splitted_details[2]
			age = splitted_details[3]
			email = splitted_details[4]

			new_user_details = {
				"username": username,
				"password": password,
				"gender": gender,
				"age": age,
				"email": email
			}

			profile_loop = False
			indexs_wrong_field = []
			if is_valid_format(username) or len(username) == 0:
				profile_loop = True
				indexs_wrong_field.append(0)
			if len(password) == 0:
				profile_loop = True
				indexs_wrong_field.append(1)
			if is_valid_format(gender) or gender.isdigit():
				profile_loop = True
				indexs_wrong_field.append(2)
			if not age.isdigit() and len(age) is not 0:
				profile_loop = True
				indexs_wrong_field.append(3)
			if not is_valid_email(email):
				profile_loop = True
				indexs_wrong_field.append(4)

			if profile_loop is True:
				server.list_of_logs.append("	({}) {}:{} <-- Wrong new credentials received.".format(get_date_and_hour(),address[0], address[1]))

				wrongdetails = ServerResponseStatus.WRONG_USER_DETAILS.value
				formatted_indexs_wrong_field = str("-".join(map(str, indexs_wrong_field)))
				msg = []
				msg.append(wrongdetails)
				msg.append(formatted_indexs_wrong_field)
				serverMessage = str(";".join(map(str, msg)))
				client_socket.send(encode_utf_8(serverMessage))

			elif not server.is_already_signed(new_user_details.get("username"), new_user_details.get("password")):
				server.save_existing_user_new_credentials(new_user_details, username_logged)

				ack = ServerResponseStatus.ACK.value
				client_socket.send(encode_utf_8(ack))
				server.list_of_logs.append("	({}) {}:{} <-- New credentials saved.".format(get_date_and_hour(), address[0],address[1],))

				profile_loop = False
				need_to_disconnect_the_client = True
			else:
				already_signed = ServerResponseStatus.EMAIL_OR_USER_ALREADY_EXISTS.value
				client_socket.send(encode_utf_8(already_signed))
				server.list_of_logs.append("	({}) {}:{} <-- New credential not saved - Username or email already exists.".format(get_date_and_hour(), address[0], address[1]))

				profile_loop = True

		elif client_reply_splitted[0] == UIText.BACK.value:

			ack = ServerResponseStatus.ACK.value
			client_socket.send(encode_utf_8(ack))
			server.list_of_logs.append(
				"	({}) {}:{} <-- No changes applied. Profile closed.".format(
					get_date_and_hour(), address[0], address[1]))
			profile_loop = False

	if need_to_disconnect_the_client or client_is_crashed:
		return True
	else:
		return False


def handle_home_screen(client_socket, address, username_logged):
	logged_loop = True
	while logged_loop is True:

		client_reply = decode_utf_8(client_socket.recv(1024))

		if is_the_reply_ctrlc(client_reply):
			server.list_of_logs.append("	({}) {}:{} --> CRASHED".format(get_date_and_hour(), address[0], address[1]))
			server.remove_connection(address[0], address[1])
			server.remove_user_from_online_list(username_logged)
			logged_loop = False

		else:
			server.list_of_logs.append("	({}) {}:{} --> {} requested.".format(get_date_and_hour(), address[0], address[1],client_reply ))

			if client_reply == UIText.PLAY_NEW_GAME.value:
				ack = ServerResponseStatus.ACK.value
				client_socket.send(encode_utf_8(ack))
				server.list_of_logs.append("	({}) {}:{} <-- ACK {}.".format( get_date_and_hour(), address[0], address[1], client_reply))

			if client_reply == UIText.PLAY_COOP_GAME.value:
				ack = ServerResponseStatus.ACK.value
				client_socket.send(encode_utf_8(ack))
				server.list_of_logs.append("	({}) {}:{} <-- ACK {}.".format(get_date_and_hour(), address[0], address[1], client_reply))

			if client_reply == UIText.CONTINUE_GAME.value:
				ack = ServerResponseStatus.ACK.value
				client_socket.send(encode_utf_8(ack))
				server.list_of_logs.append("	({}) {}:{} <-- ACK {}.".format(get_date_and_hour(), address[0], address[1], client_reply))

			if client_reply == UIText.PROFILE.value:

				need_to_disconnect_the_client_or_quit_the_loop = handle_profile_screen(client_reply, client_socket, address, username_logged)
				if need_to_disconnect_the_client_or_quit_the_loop:
					server.remove_user_from_online_list(username_logged)
					logged_loop = False

			if client_reply == UIText.LOGOUT.value:
				ack = ServerResponseStatus.ACK.value
				client_socket.send(encode_utf_8(ack))
				server.list_of_logs.append("	({}) {}:{} <-- ACK {}.".format(get_date_and_hour(), address[0], address[1], client_reply))

				server.remove_user_from_online_list(username_logged)
				logged_loop = False


def handle_sign_up_screen(client_reply, client_socket, address):
	server.list_of_logs.append("	({}) {}:{} --> {} requested.".format(get_date_and_hour(), address[0], address[1], client_reply))

	ack = ServerResponseStatus.ACK.value

	client_socket.send(encode_utf_8(ack))

	server.list_of_logs.append("	({}) {}:{} <-- ACK {}.".format(get_date_and_hour(), address[0], address[1], client_reply))

	sign_up_loop = True
	while sign_up_loop is True:

		client_reply = decode_utf_8(client_socket.recv(1024))
		server.list_of_logs.append("	({}) {}:{} --> Sign up details sent.".format(get_date_and_hour(), address[0], address[1]))

		if is_the_reply_ctrlc(client_reply):
			server.list_of_logs.append("	({}) {}:{} --> CRASHED.".format(get_date_and_hour(), address[0], address[1] ))
			server.remove_connection(address[0], address[1])
			sign_up_loop = False

		else:
			splitted_details = client_reply.split(";")

			username = splitted_details[0]
			password = splitted_details[1]
			gender = splitted_details[2]
			age = splitted_details[3]
			email = splitted_details[4]

			sign_up_loop = False
			indexs_wrong_field = []
			if is_valid_format(username) or len(username) == 0:
				sign_up_loop = True
				indexs_wrong_field.append(0)
			if len(password) == 0:
				sign_up_loop = True
				indexs_wrong_field.append(1)
			if is_valid_format(gender) or gender.isdigit():
				sign_up_loop = True
				indexs_wrong_field.append(2)
			if not age.isdigit() and len(age) is not 0:
				sign_up_loop = True
				indexs_wrong_field.append(3)
			if not is_valid_email(email):
				sign_up_loop = True
				indexs_wrong_field.append(4)


			if sign_up_loop is True:
				server.list_of_logs.append("	({}) {}:{} <-- Wrong sign up details received.".format(get_date_and_hour(),address[0], address[1]))

				wrongdetails = ServerResponseStatus.WRONG_USER_DETAILS.value
				formatted_indexs_wrong_field = str("-".join(map(str, indexs_wrong_field)))
				msg = []
				msg.append(wrongdetails)
				msg.append(formatted_indexs_wrong_field)
				serverMessage = str(";".join(map(str, msg)))
				client_socket.send(encode_utf_8(serverMessage))

			else:
				server.list_of_logs.append("	({}) {}:{} <-- Correct sign up details received.".format( get_date_and_hour(),address[0], address[1]))

				new_user_details = {
					"username": splitted_details[0],
					"password": splitted_details[1],
					"gender": splitted_details[2],
					"age": splitted_details[3],
					"email": splitted_details[4]
				}

				if not server.is_already_signed(splitted_details[0], splitted_details[4]):
					server.save_user_credentials(new_user_details)

					signed = ServerResponseStatus.SIGNED.value
					client_socket.send(encode_utf_8(signed))
					server.list_of_logs.append("	({}) {}:{} <-- Sign up completed.".format(get_date_and_hour(), address[0], address[1]))

				else:
					already_signed = ServerResponseStatus.EMAIL_OR_USER_ALREADY_EXISTS.value
					client_socket.send(encode_utf_8(already_signed))
					server.list_of_logs.append("	({}) {}:{} <-- Sign up denied - User or email already exists.".format(get_date_and_hour(), address[0], address[1]))

					sign_up_loop = True


def handle_sign_in_screen(client_reply, client_socket, address):
	server.list_of_logs.append("	({}) {}:{} --> {} requested.".format(get_date_and_hour(), address[0], address[1], client_reply))

	ack = ServerResponseStatus.ACK.value
	client_socket.send(encode_utf_8(ack))
	server.list_of_logs.append("	({}) {}:{} <-- ACK {}.".format(get_date_and_hour(), address[0], address[1], client_reply))

	client_reply = decode_utf_8(client_socket.recv(1024))
	server.list_of_logs.append("	({}) {}:{} --> Sign in credentials sent.".format(get_date_and_hour(), address[0], address[1]))

	if is_the_reply_ctrlc(client_reply):
		server.list_of_logs.append("	({}) {}:{} has disconnected: CTRL+C detected.".format(get_date_and_hour(), address[0], address[1]))
		server.remove_connection(address[0], address[1])
		server.close_client_connection(client_socket)

		msg = None

	else:

		splitted_credential = client_reply.split(";")
		username = splitted_credential[0]
		password = splitted_credential[1]

		if server.validate_user(username, password):

			if server.is_user_online(username):
				rejected = ServerResponseStatus.USER_ALREADY_ONLINE.value
				client_socket.send(encode_utf_8(rejected))
				server.list_of_logs.append("	({}) {}:{} <-- Sign in REJECTED - User already online.".format(get_date_and_hour(), address[0], address[1]))

				msg = None

			else:
				ack = ServerResponseStatus.ACK.value
				client_socket.send(encode_utf_8(ack))
				server.list_of_logs.append("	({}) {}:{} <-- Sign in VALIDATED.".format(get_date_and_hour(), address[0], address[1] ))
				server.add_user_to_online_list(username)

				msg = username
		else:
			deny = ServerResponseStatus.DENY.value
			client_socket.send(encode_utf_8(deny))
			server.list_of_logs.append("	({}) {}:{} <-- Sign in DENIED.".format(get_date_and_hour(), address[0], address[1]))

			msg = None

	return msg


def handle_client_ctrlc_request(address):
	server.list_of_logs.append("	({}) {}:{} --> CRASHED.".format(get_date_and_hour(), address[0], address[1]))
	server.remove_connection(address[0], address[1])


def handle_client_exit_request(address):
	server.list_of_logs.append("	({}) {}:{} --> DISCONNECTED.".format(get_date_and_hour(), address[0], address[1]))
	server.remove_connection(address[0], address[1])


def handle_any_exception(address, ex_message):
	server.list_of_logs.append("	({}) {}:{} : {}.".format(get_date_and_hour(),address[0], address[1], ex_message))
	server.remove_connection(address[0], address[1])


def handle_client_connection(client_socket, address):
	current_client_running = True
	try:
		while current_client_running:

			client_reply = decode_utf_8(client_socket.recv(1024))

			if is_the_reply_ctrlc(client_reply):
				handle_client_ctrlc_request(address)
				current_client_running = False

			elif is_the_reply_exit(client_reply):
				handle_client_exit_request(address)
				ack = ServerResponseStatus.ACK.value
				client_socket.send(encode_utf_8(ack))
				current_client_running = False

			elif client_reply == UIText.SIGN_UP.value:
				handle_sign_up_screen(client_reply, client_socket, address)

			elif client_reply == UIText.SIGN_IN.value:
				username = handle_sign_in_screen(client_reply, client_socket, address)
				if username:
					handle_home_screen(client_socket, address, username)

	except socket.error as sock_er:
		handle_any_exception(address, sock_er)

	except IOError as ioe:
		if ioe.errno == errno.EPIPE:
			handle_any_exception(address, ioe)
		else:
			handle_any_exception(address, ioe)
	finally:
		server.remove_connection(address[0], address[1])
		return


def handle_server_terminal_commands():
	while server.RUNNING:
		command = input("Server terminal ~/: ")

		if command == "online connections" or command == "!oc":
			server.print_online_connections()
		elif command == "online users" or command == "!ou":
			server.print_online_users()
		elif command == "show logs" or command == "!s":
			server.print_list_of_logs()
		elif command == "export logs" or command == "!e":
			write_on_file("server.log", server.list_of_logs)
			print("A server.log file has been created.")
		elif command == "clear" or command == "!ct":
			os.system("clear")
			server.print_init_stats()
			server.print_executable_commands()
		elif command == "clear logs" or command == "!cl":
			server.clear_list_of_logs()
		elif command == "":
			pass
		else:
			print("Server terminal ~/: {} not recognised".format(command))


os.system("clear")

# SIGNAL HANDLER
signal.signal(signal.SIGINT, sigint_handler)

# GLOBAL VARS
MAXIMUM_CLIENTS_CONNECTIONS = 10
server = Server()

# ARGPARSE INIT
parser = argparse.ArgumentParser()
parser.add_argument("ip", help='type the server ip address')
parser.add_argument("port", help='type the server listening port ')
args = parser.parse_args()


server.RUNNING = True
server.init_socket(args)
server.print_init_stats()
server.print_executable_commands()


threading.Thread(
	target=handle_server_terminal_commands
).start()


while server.RUNNING:
	client_socket, address = server.socket.accept()
	server.list_of_logs.append("	({}) {}:{} --> CONNECTED.".format(get_date_and_hour(), address[0], address[1]))

	lock = Lock()
	lock.acquire()

	user_handler = threading.Thread(
		target=handle_client_connection,
		args=(client_socket, address,)
	)
	user_handler.start()

	server.add_connection(user_handler, client_socket, address)
	lock.release()


