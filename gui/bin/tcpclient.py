#!/usr/bin/env python

###########
# imports
###########
import socket
import threading
import time

import client_thread
import pscdgui

###########
# init part
###########
CLIENT_THREAD = None

def start_socket(ip, port):
	global CLIENT_THREAD

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.settimeout(10)
	
	client_socket.connect((ip, port))


	CLIENT_THREAD = client_thread.ClientThread(client_socket)
	CLIENT_THREAD.daemon = True
			
	CLIENT_THREAD.start()
		
def stop_socket():
	global CLIENT_THREAD

	CLIENT_THREAD.close()

def set_state(state):
	global CLIENT_THREAD

	return CLIENT_THREAD.send_data(state, True, True)

def get_state():
	global CLIENT_THREAD

	return CLIENT_THREAD.send_data("STATUS\r\n", True, False)

def status_changed_notification(data):
	pscdgui.status_changed(data)
	
def subscribe():
	global CLIENT_THREAD

	return CLIENT_THREAD.send_data('SUBSCRIBE\r\n', True, True)

def unsubscribe():
	global CLIENT_THREAD

	return CLIENT_THREAD.send_data('UNSUBSCRIBE\r\n', True, True)
