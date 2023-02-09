import argparse
import yaml
import os
from naoqi import ALBroker
import socket
import sys

MSGLEN = 30

class Socket:

    __sock = None

    def __init__(self, sock=None):
        if sock is None:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.__sock = sock

    def connect(self, host="0.0.0.0", port=9569):
        self.__sock.connect((host, port))

    def close(self):
        self.__sock.close()

    def send(self, msg):
        self.__sock.send(msg)

    def receive(self):
        response = self.__sock.recv(4096)
        return response

class NAOConf:

    myBroker = None
    socketEnabled = False
    #sk = None

    def __init__(self, arg = argparse.ArgumentParser(), enableCommunication = False):
        arg.add_argument("--type", type=str, default="local",
                help="Robot's connection type. Default is local. Options: [wifi] [eth] [custom]")
        arg.add_argument("--ip", type=str, default="127.0.0.1",
                help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
        arg.add_argument("--port", type=int, default=9559, help="Naoqi port number")
        args = arg.parse_args()

        path = os.path.join(os.getcwd(), 'resource')

        try:
            with open(os.path.join(path, 'net.yaml')) as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
        except:
            print("Path where conf must stay: " + os.path.join(path, 'net.yaml'))
            raise Exception("Insert a .yaml file with IP configuration")

        conf = args.type
        ip = "127.0.0.1"
        port = 9559

        if conf == "custom":
            ip = args.ip
            port = args.port
        elif conf == "wifi":
            ip = data['wifi']['ip']
            port = data['wifi']['port']
        elif conf == "eth":
            ip = data['eth']['ip']
            port = data['eth']['port']

        self.ip = ip
        self.port = port

        try:
            self.myBroker = ALBroker("myBroker",
                "0.0.0.0",       # listen to anyone
                0,          	    # find a free port and use it
                self.ip,         # parent broker IP
                self.port)       # parent broker port
        except:
            raise Exception("Unable to connect to Naoqi, check the IP configuration.")

        if enableCommunication == True:
            try:
                self.sk = Socket()
                self.socketEnabled = True
            except:
                raise Exception("Unable to connect to the socket.")

    def stop(self):
        self.myBroker.shutdown()
        if self.socketEnabled == True:
            self.sk.close()

    def setSocket(self):
        self.sk.connect()
