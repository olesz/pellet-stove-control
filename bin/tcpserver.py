#!/usr/bin/env python

###########
# imports
###########
import socket
import select
import re
import threading

import state
import config


EXIT = False

def clientthread(conn):
	global EXIT

	pattern_set_load_time = re.compile('LOAD_TIME [0-9]+')
	pattern_set_load_break_time = re.compile('LOAD_BREAK_TIME [0-9]+')
	conn_ok = True

	try:
		while EXIT is False and conn_ok:
		    	ready = select.select([conn], [], [], 1)
			if ready[0]:
				command_success = True
			
				try:
					data = receive(conn).rstrip('\n').rstrip('\r')
				except RuntimeError:
					conn_ok = False

	                	if data == 'STOP':
					command_success = state.set_new_state(state.State.STOP)
				elif data == 'START':
					command_success = state.set_new_state(state.State.RUN_FORWARD)
				elif data == 'REVERSE':
					command_success = state.set_new_state(state.State.RUN_BACKWARD)
				elif data == 'STATUS':
					try:
						send(conn, "STATUS " + state.STATE["STATE"].name + " " + 
							config.get("timing","load_time") + " " + config.get("timing","load_break_time") + "\r\n")
					except RuntimeError:
						conn_ok = False
				elif pattern_set_load_time.match(data):
					config.set("timing","load_time", data.split()[1])
					config.write_config()
					command_success = True
				elif pattern_set_load_break_time.match(data):
					config.set("timing","load_break_time", data.split()[1])
					config.write_config()
					command_success = True
				else:
					command_success = False
	
				try:
					if command_success:
						send(conn, "OK\r\n")
					else:
						send(conn, "NOK\r\n")
				except RuntimeError:
					conn_ok = False

	finally:
		if conn is not None:
			conn.close()

def send(conn, msg):
	totalsent = 0
	
	while totalsent < len(msg):
		try:
			sent = conn.send(msg[totalsent:])
		except socket.error:
			raise RuntimeError("socket connection broken")
		if sent == 0:
			raise RuntimeError("socket connection broken")
		totalsent = totalsent + sent

def receive(conn):
	chunks = []
	
	pattern_line_end = re.compile('.*\r\n')
	
	while not pattern_line_end.match(''.join(chunks)):
		try:
			chunk = conn.recv(128)
		except socket.error:
			raise RuntimeError("socket connection broken")
		if chunk == '':
			raise RuntimeError("socket connection broken")
		chunks.append(chunk)
	return ''.join(chunks)	

def start_socket(ip, port):
	global EXIT

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((ip, port))
	s.setblocking(0)
	s.listen(1)

	# this part of the socket is async because if the main program exited
	# and stop_socket was called then this thread shall terminate
	while EXIT is False:
		conn = None
		try: 
			conn, addr = s.accept()
		except socket.error:
			pass

		if conn is not None:
			print 'Connection address:', addr
			client_thread = threading.Thread(target=clientthread, args=(conn,))
			client_thread.start()
	s.close()

def stop_socket():
	global EXIT

	EXIT = True
