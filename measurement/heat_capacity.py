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
        import pandas as pd

        with open(file=self.filepath, encoding='ISO-8859-1') as f:
            content = f.readlines()

        # Data start after the Line [Data].
        data_start_line = content.index('[Data]\n') + 1
        data = content[data_start_line:]
        splitted_data = [line.split(',') for line in data]

        raw_df = pd.DataFrame(data=splitted_data[1:], columns=splitted_data[0])

        # Remove the comment lines.
        df = raw_df[raw_df['Comment ()'] == '']
        # Convert all str into Floats
        df = df.apply(pd.to_numeric, errors='coerce')

        keys_to_keep = ['Time Stamp (Seconds)',
                        'Puck Temp (Kelvin)',
                        'Samp HC (µJ/K)',
                        'Samp HC/Temp (µJ/K/K)',
                        'Samp HC Err (µJ/K)',
                        'Field (Oersted)']

        # Only Keep these columns and reindex.
        df = df[keys_to_keep].reset_index(drop=True)

        return raw_df, df

    def plot(self):
        '''Create a standard plot of Heat Capacity Measurement'''
        import matplotlib.pyplot as plt
        plt.rcParams['axes.grid'] = True

        fig, ax = plt.subplots(1, 2, figsize=(12, 4), dpi=150)

        # The first graph is a Samp HC v.s. T
        ax[0].scatter(x=self.dataframe['Puck Temp (Kelvin)'],
                      y=self.dataframe['Samp HC (µJ/K)'])
        ax[0].set_xlabel('Puck Temp (Kelvin)')
        ax[0].set_ylabel('Samp HC (µJ/K)')

        ax[1].scatter(x=self.dataframe['Puck Temp (Kelvin)'],
                      y=self.dataframe['Samp HC/Temp (µJ/K/K)'])
        ax[1].set_xlabel('Puck Temp (Kelvin)')
        ax[1].set_ylabel('Samp HC/Temp (µJ/K/K)')

        fig.suptitle(f'{self.sample.name if self.sample
                        else "Unknown Sample"} under {self.field_strength} Oe')

        return fig, ax

    def __repr__(self):
        sample_name = self.sample.name if self.sample else "Unknown Sample"
        return f'HC exp, {sample_name} with {self.field_strength} Oe'
