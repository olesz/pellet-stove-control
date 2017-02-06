#!/usr/bin/env python

###########
# imports
###########
import state
import socket
import select


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

EXIT = False

def start_socket(status, config):
	global EXIT

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((TCP_IP, TCP_PORT))
	s.setblocking(0)
	s.listen(1)
	conn = None

	while EXIT is False and conn is None:
		try: 
			conn, addr = s.accept()
		except socket.error:
			#print "nothing to accept"
			pass
	
	if EXIT is False:
		print 'Connection address:', addr

	while EXIT is False:
	    	ready = select.select([conn], [], [], 1)
		if ready[0]:
   			data = conn.recv(4096).rstrip('\n').rstrip('\r')

                	if data == 'STOP':
				state.set_new_state(status, state.State.STOP)
				
			elif data == 'START':
				state.set_new_state(status, state.State.RUN_FORWARD)
			elif data == 'REVERSE':
				state.set_new_state(status, state.State.RUN_BACKWARD)

	if conn is not None:
		conn.close()
	s.close()

def stop_socket():
	global EXIT

	EXIT = True
