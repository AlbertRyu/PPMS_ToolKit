'''
This module define the [VSM_Measurement] instance,
which is a descendant of [Measurement].

VSM experiment condition:
[Sample Orientation]
'''

from .base import Measurement
from typing import TYPE_CHECKING, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from ppms_toolkit.sample import Sample  # Avoid Cylic-Import


class VSMMeasurement(Measurement):
    def __init__(self,
                 filepath: str,
                 sample_orientation: str,
                 mode: str,
                 sample: Optional["Sample"] = None,
                 comment: str = "",
                 metadata=None
                 ):
        self.sample_orientation = sample_orientation
        self.mode = mode
        super().__init__(filepath, sample, comment, metadata)
        if sample:  # If sample is inputted, add this mesurement in the sample.
            sample.add_measurement(self)

    @property
    def sample_orientation(self):
        return self._sample_orientation

    @sample_orientation.setter
    def sample_orientation(self, value):
        if value not in ("In Plane", "Out of Plane"):
            raise ValueError("sample_orientation have to be "
                             "'In Plane' or 'Out of Plane'.")
        self._sample_orientation = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in ("MH", "MT"):
            raise ValueError("Mode can only be 'MH' or 'MT'")
        self._mode = value
    
    def process_data(self, raw_df) -> pd.DataFrame:            

        df = raw_df.apply(pd.to_numeric, errors='coerce')
 
        pattern = (     
                r'^Temperature \(|'
                r'Magnetic Field \(|'
                r'Moment \(|'
                r'M. Std. Err. \('
                )
     
        cols = df.columns
        keys_to_keep = cols[cols.str.contains(pattern)]
        df = df[keys_to_keep]

        if self.mode == 'MT':
            self.const_field = np.average(df.filter(regex='Magnetic Field')).round().astype(int)
            import re
            if re.search(r'ZFC', self.filepath):
                self.condition = 'ZFC'
            elif re.search(r'FC', self.filepath):
                self.condition = 'FC'
            else:
                self.condition = 'Unknown Condition'

        else:
            self.const_temp = np.average(df.filter(regex='^Temperature')).round(1)

        return df
    
    def __repr__(self):
        if self.mode == 'MT':
            return (f'{self.mode} exp on {self.sample_name} '
                    f'with {self.sample_orientation} orientation '
                    f'at {self.const_field}Oe')
        else:
            return (f'{self.mode} exp on {self.sample_name} '
                    f'with {self.sample_orientation} orientation '
                    f'at {self.const_temp}K')
        
    def plot(self):

        fig, ax = plt.subplots()
        df = self.dataframe

        if self.mode == 'MT':
            ax.plot(df.filter(regex='^Temperature'), df.filter(regex='Moment'), label = f'{self.const_field}Oe - {self.condition}')
            ax.set_xlabel('Temperature(K)')
        elif self.mode == 'MH':
            ax.plot(df.filter(regex='Magnetic Field'), df.filter(regex='Moment'), label = f'{self.const_temp}K')
            ax.set_xlabel('Magnetic Field(Oe)')
        else:
            print('Ah oh, something went wrong. Check if measurement.mode is "MH" or "MT".')
        
        ax.set_ylabel('Moment (emu)')
        ax.set_title(f'{self.mode} - {self.sample_name} - {self.sample_orientation}')

        plt.legend()
        fig.tight_layout()

        return fig, ax
