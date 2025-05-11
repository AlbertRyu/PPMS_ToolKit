'''
This module define the HeatCapacityMeasurment instance,
which is a descendant of [Measurement].

Heat Capcity's experiment condition:
[field_strength]
'''

from .base import Measurement
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sample import Sample  # Avoid Cylic-Import


class HeatCapacityMeasurement(Measurement):
    def __init__(self,
                 filepath: str,
                 sample: "Sample" = None,
                 field_strength: float = 0.0,
                 metadata=None
                 ):
        self.field_strength = field_strength
        if sample:  # If sample is inputted, add this mesurement in the sample.
            sample.add_measurement(self)
        super().__init__(filepath, sample, metadata)

    def _load_data(self):
        with open(file=self.filepath, encoding='ISO-8859-1') as f:
            content = f.readlines()
        return content

    def __repr__(self):
        sample_name = self.sample.name if self.sample else "Unknown Sample"
        return f'HC exp, {sample_name} with {self.field_strength} Oe'
