'''
This module define the [HeatCapacityMeasurment] instance,
which is a descendant of [Measurement].

Heat Capcity's experiment condition:
[field_strength]
'''

from .base import Measurement
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.ppms_toolkit.sample import Sample  # Avoid Cylic-Import

import matplotlib.pyplot as plt
import numpy as np

from .utils import merge_by_temp_diff, debye_model_extended, debye_model

plt.rcParams['axes.grid'] = True  # Would like every plot to have grid


class HeatCapacityMeasurement(Measurement):
    def __init__(self,
                 filepath: str,
                 sample: "Sample" = None,
                 field_strength: float = 0.0,
                 comment: str = "",
                 metadata=None
                 ):
        self.field_strength = field_strength
        super().__init__(filepath, sample, comment, metadata)
        if sample:  # If sample is inputted, add this mesurement in the sample.
            sample.add_measurement(self)

    def __repr__(self):
        return (f'HC exp, {self.sample_name} '
                f'with {self.field_strength} '
                f'Oe {self.comment}')

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
                        'Sample Temp (Kelvin)',
                        'Samp HC (µJ/K)',
                        'Samp HC/Temp (µJ/K/K)',
                        'Samp HC Err (µJ/K)',
                        'Field (Oersted)']

        # Only Keep these columns and reindex.
        df = df[keys_to_keep]
        df = merge_by_temp_diff(df=df,
                                temp_col='Sample Temp (Kelvin)',
                                tol=0.01)

        return raw_df, df

    def plot(self):
        '''Create a standard plot of Heat Capacity Measurement'''
        fig, ax = plt.subplots(1, 2, figsize=(12, 4), dpi=150)

        # The first graph is a Samp HC v.s. T
        ax[0].scatter(x=self.dataframe['Sample Temp (Kelvin)'],
                      y=self.dataframe['Samp HC (µJ/K)'])
        ax[0].set_xlabel('Sample Temp (Kelvin)')
        ax[0].set_ylabel('Samp HC (µJ/K)')

        ax[1].scatter(x=self.dataframe['Sample Temp (Kelvin)'],
                      y=self.dataframe['Samp HC/Temp (µJ/K/K)'])
        ax[1].set_xlabel('Sample Temp (Kelvin)')
        ax[1].set_ylabel('Samp HC/Temp (µJ/K/K)')

        fig.suptitle(f'{self.sample_name} under {self.field_strength} Oe')

        return fig, ax

    def background_subtraction(self, mask_func=None, model=None, bounds=None):
        from scipy.optimize import curve_fit

        def default_model(T, A):
            return A * T**3 + (1-A) * T

        if not model:
            model = default_model
        if not mask_func:
            def mask_func(T):
                return np.full_like(T, True)

        T = self.dataframe['Sample Temp (Kelvin)']
        HC = self.dataframe['Samp HC (µJ/K)']

        mask = mask_func(T)
        T_fit = T[mask]
        HC_fit = HC[mask]

        params, _ = curve_fit(model, T_fit, HC_fit,
                              bounds=bounds)
        phonon_background = model(T, *params)
        subtracted = HC - phonon_background

        fig, ax = plt.subplots()

        ax.plot(T, HC, label='Heat Capacity')
        ax.plot(T, phonon_background, label='Phonon Background')
        ax.plot(T, subtracted, label='Subtracted.')
        plt.title(f'{self.sample_name} Phonon Background Subtraction')
        plt.legend()

        return T, subtracted, fig, ax, params

    def background_subtraction_debye(
            self, mask_func=lambda T: (T > 5) & (T < 300),
            bounds=([1, 0.0001],
                    [500, 100])
                    ):
        return self.background_subtraction(
            mask_func, debye_model, bounds)

    def background_subtraction_debye_extended(
            self, mask_func=lambda T: (T > 5) & (T < 300),
            bounds=([1, 0.0001, -np.inf, -np.inf],
                    [500, 100, np.inf, np.inf])
                    ):
        return self.background_subtraction(
            mask_func, debye_model_extended, bounds)
