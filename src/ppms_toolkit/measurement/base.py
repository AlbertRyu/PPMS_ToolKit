'''
This Module defined the abstracted base class [Measurement]. It serves as
a backbone for its desecendent class, [HeatCapacityMeasurment],
[Magnetism Measurement], etc.
'''
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Tuple
if TYPE_CHECKING:
    from src.ppms_toolkit.sample import Sample  # Avoid Cylic-Import

from pandas import DataFrame


class Measurement(ABC):
    def __init__(self, filepath: str,
                 sample: Optional["Sample"] = None,
                 comment: str = '',
                 metadata: Optional[dict] = None):
        self.filepath = filepath
        self.sample = sample
        self.comment = comment
        self.metadata = metadata or {}
        self.raw_dataframe, self.dataframe = self._load_data()

    @property
    def sample_name(self):
        return self.sample.name if self.sample else "Unknown Sample"

    def __eq__(self, other):
        if not isinstance(other, Measurement):
            return False
        return self.filepath == other.filepath and self.sample == other.sample

    @abstractmethod
    def _load_data(self) -> Tuple[DataFrame, DataFrame]:
        '''This Method have to be defined in the desendent class.'''
        pass
