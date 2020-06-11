from emonhub_interfacer import EmonHubInterfacer
from collections import defaultdict
import time
import atexit
import RPi.GPIO as GPIO

import Cargo

"""class EmonhubPulseCounterInterfacer

Monitors GPIO pins for pulses

"""

class EmonHubPulseCounterInterfacer(EmonHubInterfacer):

    def __init__(self, name):
        """Initialize interfacer

        """

        # Initialization
        super().__init__(name)

        self._pulse_settings = {
            'pulse_pins': '',
            'bouncetime' : 1,
        }
        self.pulse_count = defaultdict(int)

        self.init_gpio()

    def init_gpio(self):
        """Register GPIO callbacks

        """

        atexit.register(GPIO.cleanup)
        GPIO.setmode(GPIO.BOARD)
        for pin in self._settings['pulse_pins'].split(','):
            pin = int(pin)
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.process_pulse, bouncetime=int(self._settings['bouncetime']))

    def process_pulse(self, channel):
        self.pulse_count[channel] += 1
        self._log.debug('Channel %d pulse: %d', channel, self.pulse_count[channel])

    def read(self):
        t = time.time()
        f = '{t} {nodeid}'.format(t=t, nodeid=self._settings['nodeoffset'])
        for pin in self._settings['pulse_pins'].split(','):
            f += ' {}'.format(self.pulse_count[int(pin)])

        # Create a Payload object
        c = Cargo.new_cargo(rawdata=f)

        f = f.split()

        if int(self._settings['nodeoffset']):
            c.nodeid = int(self._settings['nodeoffset'])
            c.realdata = f
        else:
            c.nodeid = int(f[0])
            c.realdata = f[1:]

        return c


    def set(self, **kwargs):
        super().set(**kwargs)

        for key, setting in self._pulse_settings.items():
            if key not in kwargs:
                setting = self._pulse_settings[key]
            else:
                setting = kwargs[key]
            if key in self._settings and self._settings[key] == setting:
                continue
            elif key == 'pulse_pins':
                self._log.info("Setting %s pulse_pins: %s", self.name, setting)
                self._settings[key] = setting
                continue
            else:
                self._log.warning("'%s' is not valid for %s: %s", setting, self.name, key)
