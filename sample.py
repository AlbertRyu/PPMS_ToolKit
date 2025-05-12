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
    def __init__(self, name: str,
                 id: float = None,
                 mass: float = None,
                 make_time: str = None):
        self.name = name
        self.id = id
        self.mass = mass  # milligram
        self.make_time = \
            datetime.strptime(make_time, "%Y-%m-%d") if make_time else None
        self.measurements: list[Measurement] = []

    def set_make_time(self, make_time: str):
        self.make_time = datetime.strptime(make_time, "%Y-%m-%d")

    def add_measurement(self, m: Measurement):
        self.measurements.append(m)
        m.sample = self  # double-linked with the measurement

    def save(self):
        with open(f'id: {self.id if self.id else "None"},'
                  f'{self.name}.pkl', "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)

    def __repr__(self):
        date = self.make_time.date() if self.make_time else "Unknwon Date"
        return (f'id: {self.id}, '
                f'{self.name}, '
                f'{self.mass}mg, '
                f'made in {date}.')
