'''
This Module defined the abstracted base class [Measurement]. It serves as
a backbone for its desecendent class, [HeatCapacityMeasurment],
[Magnetism Measurement], etc.
'''
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ppms_toolkit.sample import Sample  # Avoid Cylic-Import

import pandas as pd


class Measurement(ABC):
    def __init__(self, filepath: str,
                 sample: "Sample", 
                 comment: str = '',
                 metadata: Optional[dict] = None):
        self.filepath = filepath
        self.sample = sample
        self.comment = comment
        self.metadata = metadata or {}
        self.raw_dataframe, self.dataframe = self.load_data()

    @property
    def sample_name(self):
        return self.sample.name if self.sample else "Unknown Sample"

    def load_data(self):
        try:
            with open(file=self.filepath, encoding='utf-8', errors="strict") as f:
                content = f.readlines()
        except UnicodeDecodeError:
            with open(file=self.filepath, encoding='iso-8859-1') as f:
                content = f.readlines()

        # Data start after the Line [Data].
        data_start_line = content.index('[Data]\n') + 1
        data = content[data_start_line:]
        splitted_data = [line.split(',') for line in data]

        raw_df = pd.DataFrame(data=splitted_data[1:], columns=splitted_data[0])

        df = self.process_data(raw_df)

        return raw_df, df

    def __eq__(self, other):
        from pathlib import Path
        if not isinstance(other, Measurement):
            return False
        return Path(self.filepath).resolve() == Path(other.filepath).resolve()

    @abstractmethod
    def process_data(self, raw_df) -> pd.DataFrame:
        '''This Method have to be defined in the desendent class.'''
        pass
