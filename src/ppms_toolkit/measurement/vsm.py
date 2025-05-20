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
                 sample: Optional["Sample"] = None,
                 sample_ori: float = 0.0,
                 comment: str = "",
                 metadata=None
                 ):
        self.
        super().__init__(filepath, sample, comment, metadata)
