# test_experiment.py
import pytest
from unittest.mock import Mock
from experiment import Experiment
from data_manager import DataManager

@pytest.fixture
def mock_data_manager():
    manager = DataManager('/fake/dir')
    manager.log_event = Mock()
    manager.log_quantity = Mock()
    return manager

@pytest.fixture
def mock_hardware():
    return {
        'buttons': {
            'green': Mock(),
            'blue': Mock(),
            'red': Mock()
        },
        'servo': Mock(),
        'touch_sensor': Mock()
    }

def test_experiment_initialization(mock_data_manager, mock_hardware):
    experiment = Experiment(config={}, data_manager=mock_data_manager, hardware=mock_hardware)
    assert experiment is not None

def test_experiment_run(mock_data_manager, mock_hardware):
    experiment = Experiment(config={}, data_manager=mock_data_manager, hardware=mock_hardware)
    experiment.run()
    # Assertions to check if the experiment ran correctly
    mock_data_manager.log_event.assert_called()
    mock_data_manager.log_quantity.assert_called()

# ----------- need to streamline these 2 code suggestions

# test_experiment.py
import pytest
from experiment import Experiment
from test_hardware import MockButton, MockServo, MockTouchSensor

@pytest.fixture
def mock_hardware():
    return {
        'buttons': {
            'green': MockButton(6),
            'blue': MockButton(7),
            'red': MockButton(12)
        },
        'servo': MockServo(1),
        'touch_sensor': MockTouchSensor(5)
    }

def test_experiment_run(mock_hardware):
    config = load_test_config()
    data_manager = MockDataManager(config['DATA_DIR'])
    sound_manager = MockSoundManager()
    experiment = Experiment(config, data_manager, sound_manager, mock_hardware)

    # Simulate button press
    mock_hardware['buttons']['green'].simulate_press()

    experiment.run()

    # Assert that the experiment ran as expected


class MockButton:
    def __init__(self, pin):
        self.pin = pin
        self.pressed = False

    def is_pressed(self):
        return self.pressed

    def simulate_press(self):
        self.pressed = True

    def simulate_release(self):
        self.pressed = False

# Similarly, create MockServo and MockTouchSensor classes
