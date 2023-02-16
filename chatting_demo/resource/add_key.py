import yaml
import os
import sys

def main():
    argv = sys.argv

    net_file_path = os.path.join(argv[1], "net.yaml")
    
    try:
        with open(net_file_path) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
    except:
        print("Path where conf must stay: " + net_file_path)
        raise Exception("Insert a .yaml file with IP configuration")

    cmdCreate = "mkdir /root/.ssh"
    os.system(cmdCreate)
    cmdTouch = "touch /root/.ssh/known_hosts"
    os.system(cmdTouch)

    ips = []
    for conn_type in data.keys():
        ip = data[conn_type]['ip']
        cmd = "ssh-keyscan -H " + ip + " >> ~/.ssh/known_hosts"
        os.system(cmd)  

    cmdOpenAI = "cp /root/open_ai.key " + argv[1]
    os.system(cmdOpenAI)

if __name__ == "__main__":
    main()