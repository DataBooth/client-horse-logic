from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self, data_dir, log_file_name, quantity_file_name, tts=None, echo=True, speak=False):
        self.data_dir = Path(data_dir)
        self.log_file = self.data_dir / log_file_name
        self.quantity_file = self.data_dir / quantity_file_name
        self.tts = tts
        self.echo = echo
        self.speak = speak

    def log_event(self, event_name, event_time=None, speak=None):
        if event_time is None:
            event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        log_message = f"{event_time}: {event_name}\n"
        with open(self.log_file, "a") as log:
            log.write(log_message)
        if self.echo:
            print(log_message, end="")
        if self.speak or (speak is True and self.tts is not None):
            self.tts.speak(event_name)

    def log_quantity(
        self,
        quantity_name,
        quantity_value,
        subject_name,
        trial_number,
        trainer_number,
        quantity_time=None,
    ):
        if quantity_time is None:
            quantity_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        csv_str = f"{quantity_time},{subject_name},{trial_number},{trainer_number},{quantity_name},{quantity_value}\n"
        with open(self.quantity_file, "a") as q_file:
            q_file.write(csv_str)
        if self.echo:
            print(f"Quantity recorded - {csv_str}", end="")

    # Additional methods as needed
