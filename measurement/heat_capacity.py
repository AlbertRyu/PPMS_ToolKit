'''
This module define the HeatCapacityMeasurment instance,
which is a descendant of [Measurement].

Heat Capcity's experiment condition:
[field_strength]
'''

from .base import Measurement


class HeatCapacityMeasurement(Measurement):
    def __init__(self, filepath, field_strength: float = 0.0, metadata=None):
        self.field_strength = field_strength
        super().__init__(filepath, metadata)

    def _load_data(self):
        with open(file=self.filepath, encoding='ISO-8859-1') as f:
            content = f.readlines()
        return content
