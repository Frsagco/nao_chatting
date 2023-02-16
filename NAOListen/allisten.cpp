#include "allisten.h"
#include <iostream>
#include <alcommon/albroker.h>
#include <qi/log.hpp>
#include <alaudio/alsoundextractor.h>
#include <alcommon/alproxy.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT 9579

using namespace AL;

ALListen::ALListen(boost::shared_ptr<ALBroker> broker, const std::string& name):
  ALSoundExtractor(broker, name),
  fMemoryProxy(broker)
{
  qiLogInfo("module.example") << "ALListen::costructor init." << std::endl;

  setModuleDescription("The module gives access to all trace audio comes from microphones.");

  functionName("startMicrophone", getName(), "Microphone selected starts to record.");
  BIND_METHOD(ALListen::startMicrophone);

  functionName("stopMicrophone", getName(), "Microphone selected stops to record.");
  BIND_METHOD(ALListen::stopMicrophone);

  functionName("setMicrophone", getName(), "Microphone selection.");
  addParam("microMod", "Microphone selected.");
  BIND_METHOD(ALListen::setMicrophone);

  qiLogInfo("module.example") << "ALListen::costructor done." << std::endl;
}


ALListen::~ALListen() 
{
  qiLogInfo("module.example") << "ALListen::destructor init." << std::endl;
  stopDetection();
  qiLogInfo("module.example") << "ALListen::destructor done." << std::endl;
}

void ALListen::init()
{
  qiLogInfo("module.example") << "ALListen::init init." << std::endl;

  isStarted = false;
  isSet = false;

  qiLogInfo("module.example") << "ALListen::init done." << std::endl;
}

void ALListen::startMicrophone()
{
  int valread;
  struct sockaddr_in serv_addr;
  char buffer[1024] = { 0 };
  qiLogInfo("module.example") << "ALListen::startMicrophone init." << std::endl;
  
  if (!isSet) {
    qiLogInfo("module.example") << "Please set a micro calling setMicrophone() method." << std::endl;
    return;
  }

  isStarted = true;

  startDetection();

  qiLogInfo("module.example") << "ALListen::startMicrophone done." << std::endl;
}

void ALListen::stopMicrophone()
{
  qiLogInfo("module.example") << "ALListen::stopMicrophone init." << std::endl;

  if (!isStarted) {
    qiLogInfo("module.example") << "Module is not started." << std::endl;
    return;
  }

  isStarted = false;
  // close(client_fd);
  stopDetection();
  qiLogInfo("module.example") << "ALListen::stopMicrophone done." << std::endl;
}

void ALListen::setMicrophone(const int &microMod) 
{
  qiLogInfo("module.example") << "ALListen::setMicrophone init." << std::endl;

  if (isSet && isStarted) {
    qiLogInfo("module.example") << "Module already set using a micro acquisition." << std::endl;
    return;
  }

  audioDevice->callVoid("setClientPreferences",
                      getName(),                 //Name of this module
                      16000,                     //16000 Hz requested
                      (int) microMod,            //Channels requested
                      0                          //Deinterleaving is not needed here
                      );  

  isSet = true;

  qiLogInfo("module.example") << "ALListen::setMicrophone done." << std::endl;
}

void ALListen::process(const int & nbOfChannels,
                                   const int & nbrOfSamplesByChannel,
                                   const AL_SOUND_FORMAT * buffer,
                                   const ALValue & timeStamp)
{
  /// Compute the maximum value of the front microphone signal.
  int maxValueFront = 0;

  for(int i = 0 ; i < nbrOfSamplesByChannel ; i++)
  {
    if(buffer[i] > maxValueFront)
    {
      maxValueFront = buffer[i];
    }
  }

  if(maxValueFront > 5500)
  {
    std::cout << "ALListen::process: Something detected." << std::endl;
    std::cout << "ALListen::process: LeftBumperPressed raised." << std::endl;
    fMemoryProxy.raiseEvent("LeftBumperPressed", 1.0);
  }
}

void ALListen::callback(const std::string &key, const AL::ALValue &value, const AL::ALValue &msg) 
{
  qiLogInfo("module.example") << "Callback:" << key << std::endl;
  qiLogInfo("module.example") << "Value   :" << value << std::endl;
  qiLogInfo("module.example") << "Msg     :" << msg << std::endl;
}