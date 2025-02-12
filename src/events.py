from events_manager import Event


class NewAnalysysMessagesReceivedEvent(Event):
    def __init__(self, forwarder, token):
        self.forwarder = forwarder
        self.token = token


class AnalysisStarted(Event):
    def __init__(self, forwarder, token, caller_username):
        self.forwarder = forwarder
        self.token = token
        self.caller_username = caller_username
