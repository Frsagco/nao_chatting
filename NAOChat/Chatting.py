import openai
import socket
import sys
import re
import time
import speech_recognition as sr
import os
import paho.mqtt.client as mqtt
import argparse

MSGLEN = 30

class ChatGPT():
    __isEnabled = False

    def __init__(self):
        print("ChatGPT::init: init.")

        # Define OpenAI API key
        openai.api_key = "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"
        # Set up the model and prompt
        self.model_engine = "text-curie-001"

        print("ChatGPT::init: done.")

    def chat(self, request):
        print("ChatGPT::chat: init.")

        if self.__isEnabled == False or not isinstance(request, str):
            return "I don't want to chat with you."

        completion = openai.Completion.create(
            engine=self.model_engine,
            prompt=request,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5)
        response_tmp = completion.choices[0].text

        response = re.sub('\n+', '', response_tmp)
        response = re.sub(' +', ' ', response)
        response = response.strip()

        print("ChatGPT::chat: done.")
        return response


    def enableChat(self):
        print("ChatGPT::enabled")
        self.__isEnabled = True

    def disableChat(self):
        print("ChatGPT::disabled")
        self.__isEnabled = False

class Chatting():
    def __init__(self, enable=False):
        print("Chatting::init: init")

        self.client = mqtt.Client()
        self.client.connect("0.0.0.0", 1883, 60)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.chatting_callback

        self.engine = ChatGPT()

        if enable:
            self.engine.enableChat()
        else:
            self.engine.disableChat()

        print("Chatting::init: done")


    def on_connect(self, client, userdata, flags, rc):
        print("Chatting::on_connect: Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe("nao/speech/request")

    def chatting_callback(self, client, userdata, msg):
        listInterationStr = msg.payload.decode("utf-8")

        print("Chatting::chatting_callback: Message received.")
        print("Chatting::chatting_callback: List of interation: " + listInterationStr)

        path_records = os.path.join(os.getcwd(), "records")
        audio_file = os.path.join(path_records, "rec.wav")

        # use the audio file as the audio source
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)  # read the entire audio file

        try:
            human_sentence_google = r.recognize_google(audio)
        except:
            print("Chatting::chatting_callback: Nothing recognized by Google")
            human_sentence_google = ""

        # Tensorflow try
        # try:
        #     #human_sentence = r.recognize_tensorflow(audio, tensor_graph='/naoqi/src/example_projects/tensorflow-data/conv_actions_frozen.pb', tensor_label='/naoqi/src/example_projects/tensorflow-data/conv_actions_labels.txt')
        #     human_sentence_google = r.recognize_google(audio)
        # except sr.UnknownValueError:
        #     print("Tensorflow could not understand audio")
        # except sr.RequestError as e:
        #     print("Could not request results from Tensorflow service; {0}".format(e))
        # print("Human sentence: " + human_sentence)

        human_sentence = human_sentence_google
        print("Chatting::chatting_callback: Human sentence by google: " + human_sentence)
        human_sentence = human_sentence.strip()

        if len(human_sentence) == 0:
            nao_response = "Repeat please"
        else:
            (isInterationDetected, intId) = self.detectInteration(listInterationStr, human_sentence)
            if isInterationDetected is False:
                nao_response = self.engine.chat(human_sentence)
                print("Chatting::chatting_callback: ChatGPT: " + nao_response)
            else:
                nao_response = intId
                print("Chatting::chatting_callback: Interation: " + nao_response)

        response = human_sentence + "|" + nao_response
        print("Chatting::chatting_callback: response: " + response)

        self.client.publish("nao/speech/response", response)

    def loop(self):
        self.client.loop_forever()

    def detectInteration(self, listInterationStr, human_sentence):

        flag = False
        interation = ""

        speech = human_sentence.split(" ")
        listInteration = listInterationStr.split(" ")

        for word in speech:
            try:
                idx = listInteration.index(word)
                interation = listInteration[idx]
                flag = True
            except:
                idx = -1

        return (flag, interation)
    
    def debug_str(self, message):
        print("NAOChat::debug_str: request")
        self.client.publish("nao/speech/request", message)


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--gpt", type=str, default="disable", help="Enable/Disable chat GPT. Default: disable")
    args = arg.parse_args()

    gpt = args.gpt
    gpt = gpt.strip().lower()
    mode = False

    if gpt == "enable":
        mode = True
   
    chat = Chatting(mode)
    
    try:
        chat.loop()
    except:
        print("Interrupted")
        sys.exit(0)

if __name__ == "__main__":
	main()
