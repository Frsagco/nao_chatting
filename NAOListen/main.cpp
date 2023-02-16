#include <iostream>
#include <stdlib.h>
#include <qi/os.hpp>
#include <csignal>

#include "allisten.h"

#include <alcommon/almodule.h>
#include <alcommon/albroker.h>
#include <alcommon/albrokermanager.h>

static bool loopEnabled;

class ModuleBroker {

    std::string brokerName;
    int brokerPort;
    std::string brokerIp;
    boost::shared_ptr<AL::ALBroker> broker;
    std::string pip;
    int pport;

  public:
    ModuleBroker(std::string pip, 
                  int pport, 
                  std::string brokerName, 
                  int brokerPort, 
                  std::string brokerIp) {
      
      std::cout << "ModuleBroker::constructor: init" << std::endl;
      
      this->brokerName = brokerName;
      this->brokerPort = brokerPort;
      this->brokerIp = brokerIp;
      this->pip = pip;
      this->pport = pport;
      
      loopEnabled = true;
      signal(SIGINT, this->end);
      signal(SIGTERM, this->end);

      std::cout << "ModuleBroker::constructor: done" << std::endl;
    }


    ~ModuleBroker() {
      std::cout << "ModuleBroker::destructor: init" << std::endl;

      auto modulePtr = this->broker->getModuleByName("ALListen");
      modulePtr->exit(); // try this fucking thing
      std::cout << "ModuleBroker::destructor: done" << std::endl;
    }

    int init() {
      std::cout << "ModuleBroker::init: init" << std::endl;

      try {
          this->broker = AL::ALBroker::createBroker(this->brokerName,
                                                    this->brokerIp,
                                                    this->brokerPort,
                                                    this->pip,
                                                    this->pport,
                                                    0);
        } catch(...) {
          std::cerr << "Fail to connect broker to: " << pip << ":" << pport << std::endl;

          AL::ALBrokerManager::getInstance()->killAllBroker();
          AL::ALBrokerManager::kill();

          return -1;
        }

        // Deal with ALBrokerManager singleton (add your borker into NAOqi)
        AL::ALBrokerManager::setInstance(broker->fBrokerManager.lock());
        AL::ALBrokerManager::getInstance()->addBroker(broker);

        // Now it's time to load your module with
        // AL::ALModule::createModule<your_module>(<broker_create>, <your_module>);
        AL::ALModule::createModule<ALListen>(broker, "ALListen");

        std::cout << "ModuleBroker::init: done" << std::endl;
        return 0;
    }

    void loop() {
      std::cout << "ModuleBroker::loop: init" << std::endl;
      
      while (loopEnabled)
       qi::os::sleep(1);
    }

    static void end(int sig) {
      loopEnabled = false;
    }
};



int main(int argc, char* argv[])
{
  // We will try to connect our broker to a running NAOqi
  int pport = 9559;
  std::string pip = "127.0.0.1";

  // command line parse option
  // check the number of arguments
  if (argc != 1 && argc != 3 && argc != 5)
  {
    std::cerr << "Wrong number of arguments!" << std::endl;
    std::cerr << "Usage: mymodule [--pip robot_ip] [--pport port]" << std::endl;
    exit(2);
  }

  // if there is only one argument it should be IP or PORT
  if (argc == 3)
  {
    if (std::string(argv[1]) == "--pip")
      pip = argv[2];
    else if (std::string(argv[1]) == "--pport")
      pport = atoi(argv[2]);
    else
    {
      std::cerr << "Wrong number of arguments!" << std::endl;
      std::cerr << "Usage: mymodule [--pip robot_ip] [--pport port]" << std::endl;
      exit(2);
    }
  }

  // Sepcified IP or PORT for the connection
  if (argc == 5)
  {
    if (std::string(argv[1]) == "--pport"
        && std::string(argv[3]) == "--pip")
    {
      pport = atoi(argv[2]);
      pip = argv[4];
    }
    else if (std::string(argv[3]) == "--pport"
             && std::string(argv[1]) == "--pip")
    {
      pport = atoi(argv[4]);
      pip = argv[2];
    }
    else
    {
      std::cerr << "Wrong number of arguments!" << std::endl;
      std::cerr << "Usage: mymodule [--pip robot_ip] [--pport port]" << std::endl;
      exit(2);
    }
  }
  
  // Need this to for SOAP serialization of floats to work
  setlocale(LC_NUMERIC, "C");

  ModuleBroker mb (pip, pport, "mybroker" , 54000, "0.0.0.0");

  if (mb.init() != 0)
    return -1;

  try {
    mb.loop();
  } catch(...) {
    std::cout << "Interrupted." << std::endl;
  }

  return 0;
}