#ifndef ALLISTEN_H
#define ALLISTEN_H

#include <boost/shared_ptr.hpp>
#include <alcommon/almodule.h>
#include <alaudio/alsoundextractor.h>
#include <alcommon/albroker.h>
#include <alproxies/almemoryproxy.h>



namespace AL
{
  // This is a forward declaration of AL:ALBroker which
  // avoids including <alcommon/albroker.h> in this header
  class ALBroker;
} 

/**
 * A simple example module that says "Hello world" using
 * text to speech, or prints to the log if we can't find TTS
 *
 * This class inherits AL::ALModule. This allows it to bind methods
 * and be run as a remote executable or as a plugin within NAOqi
 */

class ALListen : public AL::ALSoundExtractor
{
  public:
    ALListen(boost::shared_ptr<AL::ALBroker> pBroker, const std::string& pName);

    virtual ~ALListen();

    /** Overloading ALModule::init().
    * This is called right after the module has been loaded
    */

    void init();

    void startMicrophone();

    void stopMicrophone();

    void setMicrophone(const int &microMod);


    void process(const int & nbOfChannels,
                const int & nbrOfSamplesByChannel,
                const AL_SOUND_FORMAT * buffer,
                const AL::ALValue & timeStamp);

    void callback(const std::string &key, 
                const AL::ALValue &value, 
                const AL::ALValue &msg);

    /**
    * Make Nao say a sentence given in argument.
    */
    //void sayText(const std::string& toSay);

    /**
    * Make Nao say a sentence and return its length.
    */
    //int sayTextAndReturnLength(const std::string &toSay);
  private:
    bool isStarted; // flag set when detection is started
    bool isSet;

    int sock;
    int client_fd;

    AL::ALMemoryProxy fMemoryProxy;
};
#endif // ALLISTEN_H