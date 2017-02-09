#!/usr/bin/env python

###########
# imports
###########
import socket
import threading
import time

import client_thread

###########
# init part
###########
THREADLIST = []
LOCK = threading.RLock()

def start_socket(ip, port):
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((ip, port))
	server_socket.listen(1)

	# this part of the socket is async because if the main program exited
	# and stop_socket was called then this thread shall terminate
	while True:		
		conn, addr = server_socket.accept()
		
		client_th = client_thread.ClientThread(conn)
		client_th.daemon = True
		
		threadlist_add(client_th)
		
		client_th.start()
		
		# just for safety reasons ...
		# because thread is removed from threadlist in client_thread cleanup
		for thread in THREADLIST:
			if not thread.is_alive():
				threadlist_remove(thread)

	server_socket.close()

def threadlist_add(thread):
	LOCK.acquire()
	THREADLIST.append(thread)
	LOCK.release()

def threadlist_remove(thread):
	LOCK.acquire()
	THREADLIST.remove(thread)
	LOCK.release()

def set_notify(notify):	
	LOCK.acquire()
	
	for thread in THREADLIST:
		thread.notifyStatus()

	LOCK.release()
