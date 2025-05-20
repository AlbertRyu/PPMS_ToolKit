'''
This module define the [VSM_Measurement] instance,
which is a descendant of [Measurement].

VSM experiment condition:
[Sample Orientation]
'''

from .base import Measurement
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from src.ppms_toolkit.sample import Sample  # Avoid Cylic-Import


class VSMMeasurement(Measurement):
    def __init__(self,
                 filepath: str,
                 sample_orientation: str,
                 sample: Optional["Sample"] = None,
                 comment: str = "",
                 metadata=None
                 ):
        self.sample_orientation = sample_orientation
        super().__init__(filepath, sample, comment, metadata)

    @property
    def sample_orientation(self):
        return self._sample_orientation

    @sample_orientation.setter
    def sample_orientation(self, value):
        if value not in ("In Plane", "Out of Plane"):
            raise ValueError("sample_orientation have to be "
                             "'In Plane' or 'Out of Plane'.")
        self._sample_orientation = value
