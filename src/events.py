from events_manager import Event


class TokenAnalyzedEvent(Event):
    def __init__(self, forwarder, contract_address, analyzer_username, analyzer_message):
        self.forwarder = forwarder
        self.contract_address = contract_address
        self.analyzer_username = analyzer_username
        self.analyzer_message = analyzer_message
