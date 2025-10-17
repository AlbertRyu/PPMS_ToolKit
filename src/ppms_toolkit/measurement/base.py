'''
This Module defined the abstracted base class [Measurement]. It serves as
a backbone for its desecendent class, [HeatCapacityMeasurment],
[Magnetism Measurement], etc.
'''
from abc import ABC, abstractmethod
from multiprocessing.context import assert_spawning
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ppms_toolkit.sample import Sample  # Avoid Cylic-Import

import pandas as pd


class Measurement(ABC):
    def __init__(self, 
                 sample: "Sample", 
                 comment: str = '',
                 metadata: Optional[dict] = None,
                 filepath: str | None = None, 
                 raw_dataframe: pd.DataFrame | None = None,  # 允许直接传入
                 processed_dataframe: pd.DataFrame | None = None):
        self.filepath = filepath
        self.sample = sample
        self.comment = comment
        self.metadata = metadata or {}

        # 如果传入了 DataFrame，直接使用
        if processed_dataframe is not None and raw_dataframe is not None:
            self.raw_dataframe = raw_dataframe
            self.dataframe = processed_dataframe
        # 否则从文件加载
        elif filepath is not None:
            self.raw_dataframe, self.dataframe = self.load_data()
        else:
            raise ValueError("Must provide either 'filepath' or 'raw_dataframe'")

    @property
    def sample_name(self):
        return self.sample.name if self.sample else "Unknown Sample"

    def load_data(self):
        assert self.filepath is not None
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

        df = self.process_data(raw_df, self.filepath)

        return raw_df, df

    '''
    # Depracated function , Now Filepath is optional and unique check is depend on the sqlite

    def __eq__(self, other):
        from pathlib import Path
        if not isinstance(other, Measurement):
            return False
        return Path(self.filepath).resolve() == Path(other.filepath).resolve()
    '''

    @abstractmethod
    def process_data(self, raw_df, filepath) -> pd.DataFrame:
        '''This Method have to be defined in the desendent class.'''
        pass
