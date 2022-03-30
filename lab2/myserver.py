import sys
from ex2utils import Server

# Create a server class
class MyServer(Server):
    def onStart(self):
        print("Server connected")
    
    def onConnect(self, socket):
        print("Client has connected")
        socket.send(b"Client connected"b"\n")

    def onDisconnect(self, socket):
        print("Client has Disconnected")
        socket.send(b"Client Disconnected"b"\n")

    def onMessage(self, socket, message):
        print("Message was sent")
        socket.send(b"Message Recieved"b"\n")
        return True

# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create an echo server.
server = MyServer()

# Start server
server.start(ip, port)
