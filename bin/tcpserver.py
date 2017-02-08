#!/usr/bin/env python

###########
# imports
###########
import socket
import threading
import time

import clientThread

###########
# init part
###########
THREADLIST = []
LOCK = threading.RLock()

def start_socket(ip, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((ip, port))
	s.listen(1)

	# this part of the socket is async because if the main program exited
	# and stop_socket was called then this thread shall terminate
	while True:		
		conn, addr = s.accept()
		
		print 'Connection address:', addr
		client_thread = clientThread.ClientThread(conn)
		client_thread.daemon = True
		
		LOCK.acquire()
		THREADLIST.append(client_thread)
		LOCK.release()
		
		client_thread.start()

		for thread in THREADLIST:
			if not thread.is_alive():
				LOCK.acquire()
				THREADLIST.remove(thread)
				LOCK.release()

	s.close()

def set_notify(notify):	
	LOCK.acquire()
	
	for thread in THREADLIST:
		thread.notifyStatus()

	LOCK.release()
