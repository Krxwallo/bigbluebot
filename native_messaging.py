#!/usr/bin/env python
import json
import struct
import sys
from threading import Thread


class NativeMessagingThread(Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    @staticmethod
    def _getMessage():
        #print("Waiting for next message.")
        rawLength = sys.stdin.buffer.read(4)
        #print("Length is: " + str(rawLength))
        if len(rawLength) == 0:
            sys.exit(0)
        messageLength = struct.unpack('@I', rawLength)[0]
        message = sys.stdin.buffer.read(messageLength).decode('utf-8')
        #print("Read message:" + str(message))
        return json.loads(message)

    # Encode a message for transmission,
    # given its content.
    @staticmethod
    def _encodeMessage(messageContent):
        encodedContent = json.dumps(messageContent).encode('utf-8')
        encodedLength = struct.pack('@I', len(encodedContent))
        return {'length': encodedLength, 'content': encodedContent}

    # Send an encoded message to stdout
    @staticmethod
    def _sendMessage(encodedMessage):
        sys.stdout.buffer.write(encodedMessage['length'])
        sys.stdout.buffer.write(encodedMessage['content'])
        sys.stdout.buffer.flush()

    def run(self):
        self.loop()

    def loop(self):
        while True:
            receivedMessage = self._getMessage()
            print("Received message: " + receivedMessage)
            if receivedMessage == "ping":
                print(self._encodeMessage("Hello there"))
            self.queue.put(receivedMessage)

    def stop(self):
        pass


#print("Starting thread.")
#NativeMessagingThread().loop()
#print("Thread stopped.")
