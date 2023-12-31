"""

IRC client exemplar.

"""

import sys
from ex2utils import Client

import time


class IRCClient(Client):

	def onMessage(self, socket, message):
		# *** process incoming messages here ***
		print(message)
		return True
	
	def onStart(self):
		print("Client Started")
		pass

	def onStop(self):
		print("Client Stopped")
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

#send message to the server
message = "hello world"
client.send(message.encode())

#stops client
client.stop()
