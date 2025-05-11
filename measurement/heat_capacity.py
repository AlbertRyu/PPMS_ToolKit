'''
This module define the HeatCapacityMeasurment instance,
which is a descendant of [Measurement]
'''
import pandas as pd

from .base import Measurement


class HeatCapacityMeasurement(Measurement):
    def _load_data(self):
        data = pd.read_csv(self.filepath)
        return data
