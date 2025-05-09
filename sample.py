'''
This modules defined each sample, their properties
and their supported functions.
'''

import pickle


class Sample:
    def __init__(self, name, mass=None, make_time=None):
        self.name = name
        self.mass = mass
        self.make_time = make_time

    def selfIntroduction(self):
        print(f'Hi I am {self.name}')

    def save(self):
        with open(f"{self.name}.pkl", "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
