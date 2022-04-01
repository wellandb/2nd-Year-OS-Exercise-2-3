import sys

from numpy import partition
from ex2utils import Server

# Create a server class
class MyServer(Server):

    # Init with number of clients and a dictionary for users with their names
    def __init__(self):
        super().__init__()
        # Stores number of clients
        self.noClients = 0
        # Dictionary stores socket : username for registered users
        self.users = {}

    # Print to the server that it has started
    def onStart(self):
        print("Server connected")
    
    # Print to the server that a client has connected
    def onConnect(self, socket):
        print("Client has connected")
        # Increase number of clients connected and print
        self.noClients += 1
        print("Number of Clients connected: "+str(self.noClients))
        socket.send(b"Client connected"b"\n")

    # Print that client has disconnected
    def onDisconnect(self, socket):
        print("Client has Disconnected")
        self.noClients -= 1
        print("Number of Clients connected: "+str(self.noClients))
        socket.send(b"Client Disconnected"b"\n")
        # Tell Users that client has Disconnected

        for i in self.users.keys():
            if not(i == socket) and socket in self.users.keys():
                i.send(self.users[socket].encode() + b" has Disconnected."b"\n")
        # Remove user from list of users
        if socket in self.users.keys():
            self.users.pop(socket)

    # When a message happens
    def onMessage(self, socket, message):
        # Get Message
        (command, sep, parameter) = message.strip().partition(' ')

        # See if command is directed at a user
        (target, sep2, txt) = parameter.partition(' ')
        if target in self.users.values():
            parameter = txt
        else:
            target = 0

        # Commands
        # Register a username
        if command == "REGISTER":
            # if name taken try again
            if target != 0:
                socket.send(b"Name already registered, try again with a new one"b"\n")
                return True
            # Add username and socket to users dictionary
            self.users[socket] = parameter
            # Tell server client has registered
            print("Client " + parameter + " has connected")
            socket.send(parameter.encode()+b" Registered"b"\n")
            # Tell Users that client has registered
            for i in self.users.keys():
                if not(i == socket):
                    i.send(b"\n"+parameter.encode() + b" has registered."b"\n")
            return True
        # HELP Command
        elif command == "HELP":
            # List of commands to help user
            socket.send(b"--------------------------------------------"b"\n")
            socket.send(b"Must Register a name to Message."b"\n")
            socket.send(b"You can type commands like this:"b"\n")
            socket.send(b"<COMMAND> <PARAMETER>"b"\n")
            socket.send(b"List of Commands:"b"\n")
            socket.send(b"Register a name -REGISTER <NAME> "b"\n")
            socket.send(b"List of Registered names -LIST"b"\n")
            socket.send(b"Sends Message Content to all -MESSAGE <MESSAGE CONTENT> "b"\n")
            socket.send(b"Sends Message Content to specific person -MESSAGE <NAME> <MESSAGE CONTENT> "b"\n")
            socket.send(b"Disconnects the client, also try ^] -QUIT"b"\n")
            socket.send(b"--------------------------------------------"b"\n")
            return True
        # List command
        elif command == "LIST":
            # Returns list of registered users
            socket.send(b'\n'b"--------------------------------------------")
            socket.send(b"List of Registered Users:"b"\n")
            for i in self.users:
                socket.send(self.users[i].encode())
            socket.send(b"--------------------------------------------"b"\n")
            return True
        # Message Command
        # Public message if no target and registered
        elif command == "MESSAGE" and socket in self.users and target == 0:
            print("Message was sent:")
            msg = self.users[socket] + ": " + parameter
            print(msg)
            # Tell user message was recieved
            socket.send(b"Message Recieved"b"\n")
            # Send to other Users
            for i in self.users.keys():
                if not(i == socket):
                    i.send(b"\n"b"Public Message")
                    i.send(msg.encode())
            return True
        # Private Message Command if there is a target
        elif command == "MESSAGE" and socket in self.users and target != 0:
            print("Private Message was sent:")
            print(self.users[socket] + " to " + target)
            msg = self.users[socket] + ": " + parameter
            socket.send(b"Message Recieved"b"\n")
            # Send to target
            for i in self.users.keys():
                # Check if target
                if self.users[i] == target:
                    i.send(B"\n"b"Private Message")
                    i.send(msg.encode())
            return True
        # If Users aren't Registered
        elif command == "MESSAGE":
            socket.send(b"Not Registered try: REGISTER or HELP")
            return True
        # Quit if '^]'
        elif command == "^]" or command == "QUIT":
            return False
        else:
            socket.send(b"Unknown Command try: HELP")
            return True

# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create an echo server.
server = MyServer()

# Start server
server.start(ip, port)
