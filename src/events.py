from events_manager import Event


class TokenAnalyzedEvent(Event):
    def __init__(self, contract_address, analyzer_username, analyzer_message):
        self.contract_address = contract_address
        self.analyzer_username = analyzer_username
        self.analyzer_message = analyzer_message
