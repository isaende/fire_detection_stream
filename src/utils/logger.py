# Gerenciamento de histórico de eventosimport collections
import collections
from datetime import datetime

class EventLogger:
    def __init__(self, max_logs=8):
        # initialize a deque to store logs with a maximum length to automatically discard the oldest logs when the limit (max_logs) is reached.
        self.logs = collections.deque(maxlen=max_logs)

    def add_event(self, label, confidence):
        """
        Registers a new event in the log with a timestamp, label, and confidence percentage.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_entry = f"[{timestamp}] {label} ({confidence * 100:.0f}%)"
        
        # Add the new log entry to the left of the deque, so the most recent events are at the front.
        self.logs.appendleft(log_entry)

    def get_logs(self):
        """
    Returns a list of the current logs, with the most recent events first.
        """
        return list(self.logs)