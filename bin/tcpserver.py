#!/usr/bin/env python

###########
# imports
###########
import socket
import select
import re

import state
import config

TCP_IP = '127.0.0.1'
TCP_PORT = 5005

EXIT = False

def send(conn, msg):
	totalsent = 0
	
	while totalsent < len(msg):
		sent = conn.send(msg[totalsent:])
		if sent == 0:
			raise RuntimeError("socket connection broken")
		totalsent = totalsent + sent

def receive(conn):
	chunks = []
	
	pattern_line_end = re.compile('.*\r\n')
	
	while not pattern_line_end.match(''.join(chunks)):
		chunk = conn.recv(128)
		if chunk == '':
			raise RuntimeError("socket connection broken")
		chunks.append(chunk)
	return ''.join(chunks)	

def start_socket(ip, port):
	global EXIT

	pattern_set_load_time = re.compile('LOAD_TIME [0-9]+')
	pattern_set_load_break_time = re.compile('LOAD_BREAK_TIME [0-9]+')

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((ip, port))
	s.setblocking(0)
	s.listen(1)
	conn = None

	# this part of the socket is async because if the main program exited
	# and stop_socket was called then this thread shall terminate
	while EXIT is False and conn is None:
		try: 
			conn, addr = s.accept()
		except socket.error:
			pass
	
	if EXIT is False:
		print 'Connection address:', addr

	while EXIT is False:
	    	ready = select.select([conn], [], [], 1)
		if ready[0]:
			command_success = True
			data = receive(conn).rstrip('\n').rstrip('\r')

                	if data == 'STOP':
				command_success = state.set_new_state(state.State.STOP)
			elif data == 'START':
				command_success = state.set_new_state(state.State.RUN_FORWARD)
			elif data == 'REVERSE':
				command_success = state.set_new_state(state.State.RUN_BACKWARD)
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
			
			if command_success:
				send(conn, "OK\r\n")
			else:
				send(conn, "NOK\r\n")
	if conn is not None:
		conn.close()
	s.close()

def stop_socket():
	global EXIT

	EXIT = True
