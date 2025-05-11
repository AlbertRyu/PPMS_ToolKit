'''
This modules defined each sample, their properties
and their supported functions.

The Samples should contains serveal Measurement and could
be save into a .pickel file and reload some time again.
'''

import pickle
from datetime import datetime

from measurement import Measurement


class Sample:
    def __init__(self, name: str, mass: float = None, make_time: str = None):
        self.name = name
        self.mass = mass
        self.make_time = \
            datetime.strptime(make_time, "%Y-%m-%d") if make_time else None
        self.measurements: list[Measurement] = []

    def set_make_time(self, make_time: str):
        self.make_time = datetime.strptime(make_time, "%Y-%m-%d")

    def selfIntroduction(self):
        print(f'Hi I am {self.name}')

    def add_measurement(self, Filepath):
        pass

    def save(self):
        with open(f"{self.name}.pkl", "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
