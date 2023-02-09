from naoqi import ALProxy
from NAOConf import NAOConf
import argparse
import os
import time

class NAOMicrophone():

    def __init__(self, conf):
        self.microPxy = ALProxy("ALAudioRecorder")
        self.isRecording = False
        self.conf = conf

    def record(self):
        # start recording for 3/4 seconds until now
        path = os.path.join(os.getcwd(), 'records')

        path_intoNao = "/home/nao/rec.wav"
        self.isRecording = True
        self.microPxy.startMicrophonesRecording(path_intoNao, "wav", 16000, [0, 0, 1, 0])

        # waits the user finish to talk
        time.sleep(3)

        # stop recording, the file is in the folder ".records"
        self.microPxy.stopMicrophonesRecording()
        self.isRecording = False

        # TEMP SOLUTION
        # cmd = "sshpass -p 'nao' scp nao@" + self.conf.ip + ":/home/nao/rec.wav /naoqi/src/example_projects/records"
        cmd = "sshpass -p 'nao' scp nao@" + self.conf.ip + ":" + path_intoNao + " " + path
        os.system(cmd)

    def stopRecord(self):
        if self.isRecording == True:
            self.microPxy.stopMicrophonesRecording()
            self.isRecording = False

def main():

    conf = NAOConf(argparse.ArgumentParser())
    port = conf.port
    ip = conf.ip
    yes = 'yes'

    # mic = NAOMicrophone(conf)
    # mic.record()


    #isSeatedStr = input("Nao is seated? yes|no ")
    # if isSeatedStr.strip().lower() == yes:
    # posture = ALProxy("ALRobotPosture", ip, port)
    # posture.goToPosture("Stand", 80/100.)

    motion = ALProxy("ALMotion", ip, port)
    motion.rest()

    recordMicro = ALProxy("ALAudioRecorder", ip, port)
    recordMicro.stopMicrophonesRecording()

    memory = ALProxy("ALMemory", ip, port)
    memory.unsubscribeToEvent("SpeechDetected", "SpeechRecognition")




if __name__ == "__main__":
    main()
