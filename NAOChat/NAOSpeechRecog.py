from naoqi import ALProxy
from naoqi import ALModule
from NAOInteract import NAOAnimation
from NAOConf import NAOConf
import argparse
import time
import socket
import sys
import os
import wave
import stat
from datetime import datetime
import paho.mqtt.client as mqtt


speechRecogition = None
memory = None

class NAOMicrophone():

    def __init__(self, conf):
        print("NAOMicrophone::costructor: init")

        self.audioPlayerPxy = ALProxy("ALAudioPlayer")
        self.microPxy = ALProxy("ALAudioRecorder")
        self.ledsPxy = ALProxy("ALLeds")
        self.ledsPxy.setIntensity("FaceLeds", 0.5)

        self.recordTime = 3
        self.isRecording = False
        self.conf = conf
        self.audioIdUp = self.audioPlayerPxy.loadFile("/home/nao/sound_start_rec.wav")
        self.audioIdDown = self.audioPlayerPxy.loadFile("/home/nao/sound_stop_rec.wav")

        print("NAOMicrophone::costructor: done")


    def record(self):
        print("NAOMicrophone::record: init")

        # start recording for 3/4 seconds until now
        path = os.path.join(os.getcwd(), 'records')
        
        # current_dateTime = str(datetime.now())
        # tmp = current_dateTime.replace(' ', '_').replace(':', '').replace('.', '')
        # file_name = "record_" + tmp + ".wav"

        path_intoNao = "/home/nao/rec.wav"
        self.isRecording = True
        self.microPxy.startMicrophonesRecording(path_intoNao, "wav", 16000, [0, 1, 0, 0])
        self.ledsPxy.setIntensity("FaceLeds", 1.0)
        self.audioPlayerPxy.play(self.audioIdUp)
        
        # waits the user finish to talk
        time.sleep(self.recordTime)

        # stop recording, the file is in the folder ".records"
        self.microPxy.stopMicrophonesRecording()
        self.isRecording = False
        self.audioPlayerPxy.play(self.audioIdDown)
        self.ledsPxy.setIntensity("FaceLeds", 0.5)

        # TEMP SOLUTION
        # cmd = "sshpass -p 'nao' scp nao@" + self.conf.ip + ":/home/nao/rec.wav /naoqi/src/example_projects/records"
        cmd = "sshpass -p 'nao' scp nao@" + self.conf.ip + ":" + path_intoNao + " " + path
        os.system(cmd)

        print("NAOMicrophone::record: done")

    def stopRecord(self):
        print("NAOMicrophone::stopRecord: init")

        if self.isRecording == True:
            self.microPxy.stopMicrophonesRecording()
            self.isRecording = False
       
        print("NAOMicrophone::record: done")

class NAOSpeechRecog(ALModule):
    words = ["hi", "hello nao", "meteo", "tell me a joke"]

    def __init__(self, name, conf):
        print("NAOSpeechRecog::costructor init")

        ALModule.__init__(self, name)
        global memory
        memory = ALProxy("ALMemory")

        self.conf = conf

        self.tts = ALProxy("ALTextToSpeech")
        self.tts.setLanguage("English")
        self.tts.setVolume(0.3)

        self.faceRecog = ALProxy("ALFaceDetection")

        self.photoCaptureProxy = ALProxy("ALPhotoCapture")
        self.photoCaptureProxy.setResolution(2)
        self.photoCaptureProxy.setPictureFormat("jpg")

        self.soundDetection = ALProxy("ALSoundDetection")
        self.soundDetection.setParameter("Sensibility", 0.7)

        self.animation = NAOAnimation()

        self.microphone = NAOMicrophone(conf)

        # self.client = mqtt.Client()
        # self.client.on_connect = self.on_connect
        # self.client.on_message = self.somethingRecognized_callback
        # self.client.connect("mqtt.eclipseprojects.io", 1883, 60)
        self.client = mqtt.Client()
        self.client.connect("0.0.0.0", 1883, 60)
        self.client.on_connect = self.paho_connect
        self.client.on_message = self.speech_callback

        self.subscribe()

        self.listenMicro = ALProxy("ALListen")
        self.listenMicro.setMicrophone(4)
        self.listenMicro.startMicrophone()

        print("NAOSpeechRecog::costructor done")
        self.isSpeechEnabled = True


    def paho_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe("nao/speech/response")

    def subscribe(self):
        print("NAOSpeechRecog::subscribe: init")

        memory.subscribeToEvent("LeftBumperPressed",
            "speechRecogition",
            "somethingRecognized_callback")
        memory.subscribeToEvent("RightBumperPressed",
            "speechRecogition",
            "somethingRecognized_callback")

        print("NAOSpeechRecog::subscribe: done")


    def unsubscribe(self):
        print("NAOSpeechRecog::unsubscribe: init")
       
        memory.unsubscribeToEvent("LeftBumperPressed", "speechRecogition")
        memory.unsubscribeToEvent("RightBumperPressed", "speechRecogition")

        print("NAOSpeechRecog::unsubscribe: done")
        

    def stop(self):
        print("NAOSpeechRecog::stop: init")

        self.listenMicro.stopMicrophone()
        self.microphone.stopRecord()
        self.animation.stopMotion()

        if self.isSpeechEnabled == True:
            self.unsubscribe()

        print("NAOSpeechRecog::stop: done")


    def somethingRecognized_callback(self, *_args):
        self.unsubscribe()
        print("NAOSpeechRecog::something_callback: Unsubscribed.")

        self.isSpeechEnabled = False
        print("NAOSpeechRecog::something_callback: Recording...")
        self.microphone.record()

        # trigger SpeechDetection in the python3 script
        print("NAOSpeechRecog::something_callback: List of interaction sent: " + self.animation.getInterationList())
        self.client.publish("nao/speech/request", self.animation.getInterationList())


    def speech_callback(self, client, userdata, msg):
        print("NAOSpeechRecog::speech_callback: Message arrived")
        response = msg.payload

        response_str = response.strip()
        print("NAOSpeechRecog::speech_callback: Nao response: " + response_str)
        response_split = response_str.split("|")
        input_human = response_split[0]
        output_nao = response_split[1]

        # qui aziona le robe predefinite
        if output_nao in self.animation.getInterationList().split(" "):
            print("Action: " + output_nao)
            self.animation.play(output_nao)
        else:
            idMemoryTts = self.tts.post.say(output_nao)
            self.tts.wait(idMemoryTts, 0)
        
        self.subscribe()
        print("NAOSpeechRecog::speech_callback: Subscribed")
        self.isSpeechEnabled = True

    def loop(self):
        self.client.loop_forever()

def main():
    try:
        conf = NAOConf(argparse.ArgumentParser())
    except Exception as e:
        print(e)
        sys.exit(0)

    global speechRecogition
    speechRecogition = NAOSpeechRecog("speechRecogition", conf)

    try:
        speechRecogition.loop()
    except:
        print
        print("Interrupted")
        speechRecogition.stop()
        conf.stop()
        sys.exit(0)

if __name__ == "__main__":
	main()
