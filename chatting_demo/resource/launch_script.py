import yaml
import os
import sys

# I know, this code sucks

def main():

    net_file_path = "/root/chat_demo/nao_chatting/NAOChat/resource/net.yaml"

    try:
        with open(net_file_path) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
    except:
        print("Path where conf must stay: " + net_file_path)
        raise Exception("Insert a .yaml file with IP configuration")

    ips = []
    for conn_type in data.keys():
        ip = data[conn_type]['ip']
        if True if os.system("ping -c 1 " + ip) is 0 else False:
            cmdModule = "/root/chat_demo/nao_chatting/NAOListen/bin/./allisten --pip " + ip + " --pport 9559 &"
            os.system(cmdModule) 

            cmdChat = "python3.8 /root/chat_demo/nao_chatting/NAOChat/Chatting.py --gpt enable &"
            os.system(cmdChat)

            cmdSpeechRecog = "python2.7 /root/chat_demo/nao_chatting/NAOChat/NAOSpeechRecog.py --type " + conn_type
            os.system(cmdSpeechRecog) 

            break

if __name__ == "__main__":
    main()