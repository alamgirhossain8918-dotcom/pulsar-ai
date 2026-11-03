class PulsarException(Exception):
    """Base exception for Pulsar AI"""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class DataProviderException(PulsarException):
    """Raised when market data provider fails or returns invalid data"""
    pass


class InsufficientCandlesException(PulsarException):
    """Raised when not enough candles are available for ICT/SMC calculation"""
    pass


class SignalExecutionException(PulsarException):
    """Raised when error occurs during signal generation or lifecycle handling"""
    pass


class InvalidOrderException(PulsarException):
    """Raised when paper trading order is invalid"""
    pass
