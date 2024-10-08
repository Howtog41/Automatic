# forwarding.py

class ForwardingTask:
    def __init__(self, source_channel, destination_channel, message_limit, delay):
        self.source_channel = source_channel
        self.destination_channel = destination_channel
        self.message_limit = message_limit
        self.delay = delay
        self.active = True

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def update(self, source_channel=None, destination_channel=None, message_limit=None, delay=None):
        if source_channel:
            self.source_channel = source_channel
        if destination_channel:
            self.destination_channel = destination_channel
        if message_limit:
            self.message_limit = message_limit
        if delay:
            self.delay = delay
