'''
This Module defined the abstracted base class [Measurement]. It serves as
a backbone for its desecendent class, [HeatCapacityMeasurment],
[Magnetism Measurement], etc.
'''
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sample import Sample  # Avoid Cylic-Import


class Measurement(ABC):
    def __init__(self, filepath: str,
                 sample: "Sample" = None,
                 metadata: dict = None):
        self.filepath = filepath
        self.sample = sample
        self.metadata = metadata or {}
        self.data = self._load_data()

    @abstractmethod
    def _load_data(self):
        '''This Method have to be defined in the desendent class.'''
        pass
