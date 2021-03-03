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
        rawLength = sys.stdin.buffer.read(4)
        if len(rawLength) == 0:
            sys.exit(0)
        messageLength = struct.unpack('@I', rawLength)[0]
        message = sys.stdin.buffer.read(messageLength).decode('utf-8')
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
                print("Hello there")
            if self.queue.empty():
                print("Queue is already empty")
            else:
                print("Queue is not empty. (" + str(self.queue.qsize()) + ")")
            self.queue.put(receivedMessage)

    def stop(self):
        pass
