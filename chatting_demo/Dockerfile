FROM frsagco/naoqi1.14.5-64b:latest

RUN apt-get update && \
    mkdir /root/chat_demo && \
    cd /root/chat_demo && \
    apt-get install -y git && \
    pip3 install vcstool && \
    echo "\
        repositories: \n\
            nao_chatting: \n\
                type: git \n\
                url: https://github.com/Frsagco/nao_chatting.git \n\
        " > overlay.repos && \
    vcs import ./ < overlay.repos && cd /

ADD resource/* /root/

RUN pip3 install SpeechRecognition && \
    pip3 install openai && \
    pip3 install paho-mqtt

RUN pip2 install paho-mqtt

RUN apt-get install -y ssh && \
    apt-get install -y iputils-ping && \
    python2.7 /root/add_key.py /root/chat_demo/nao_chatting/NAOChat/resource && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /root/chat_demo/nao_chatting/NAOChat
ENTRYPOINT [ "/root/entry_point.sh" ]