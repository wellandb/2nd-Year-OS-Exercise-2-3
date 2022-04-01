import sys
from ex2utils import Client

import time


class IRCClient(Client):

	def onMessage(self, socket, message):
		# *** process incoming messages here ***
		print("\n" + str(message) + "\n")
		
        # Get Message
		(command, sep, parameter) = message.strip().partition(' ')

		# checks for incoming messages that will interrupt the enter command
		# check for message
		if command[-1] == ":":
			print("Enter Command:")
		# check for register
		elif parameter[0:3] == "has":
			print("Enter Command:")

		return True

	def onStart(self):
		print("Client Started")
		pass

	def onStop(self):
		pass
		
	def onJoin(self):
		self.stop()


# Parse the IP address and port you wish to connect to.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create an IRC client.
client = IRCClient()

# Start server
client.start(ip, port)
time.sleep(0.5)


# Main loop 
run = True
while run:
	# Asks for message input
	message = input("Enter Command: \n")
	# exit if quit command given
	if message == "^]" or message == "QUIT":
		run = False
	# send message
	client.send(message.encode())


# Stop server
client.stop()