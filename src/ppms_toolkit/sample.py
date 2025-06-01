'''

'''

import pickle
from datetime import date
from typing import Optional
from .measurement import Measurement


class Sample:
    '''
    This modules defined each sample, their properties
    and their supported functions.

    The Samples should contains serveal Measurement and could
    be save into a .pickel file and reload some time again.


    Parameters
    ----------
    name : str
        Name of the sample.
    mass : float, optional
        Mass of the sample, unit is mg.
    id   : float, optional
        Assign a unique id to the sample.
    make_date: str
        make date of the sample, in "%Y-%m-%d" format.


    Attributes
    ----------
    measurements: list
        a list of measurements assigned to this sample.
     All the parameters.
    '''
    def __init__(self, name: str,
                 id: Optional[float] = None,
                 mass: Optional[float] = None,
                 make_date: Optional[str] = None):
        self.name = name
        self.id = id
        self.mass = mass  # milligram
        self.make_date = \
            date.fromisoformat(make_date) if make_date else None
        self.measurements: list[Measurement] = []

    def set_make_date(self, make_date: str):
        self.make_date = date.fromisoformat(make_date)

    def add_measurement(self, m: Measurement):
        if m not in self.measurements:
            self.measurements.append(m)
            m.sample = self  # double-linked with the measurement
        else:
            print(f'The Measurment [{m}] \n'
                  f'is already exist in sample [{self}] ')

    def save(self):
        with open(f'{self.name}'
                  f'({self.make_date if self.make_date else "Unknown MakeTime"}).pkl', "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)

    def __repr__(self):
        date = self.make_date if self.make_date else "Unknwon Date"
        return (f'id: {self.id}, '
                f'{self.name}, '
                f'{self.mass}mg, '
                f'made in {date}.')
