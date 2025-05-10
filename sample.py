'''
This modules defined each sample, their properties
and their supported functions.
'''

import pickle
from datetime import datetime


class Sample:
    def __init__(self, name: str, mass: float = None, make_time: str = None):
        self.name = name
        self.mass = mass
        self.make_time = datetime.strptime(make_time, "%Y-%m-%d")

    def set_make_time(self, make_time: str):
        self.make_time = datetime.strptime(make_time, "%Y-%m-%d")

    def selfIntroduction(self):
        print(f'Hi I am {self.name}')

    def save(self):
        with open(f"{self.name}.pkl", "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
