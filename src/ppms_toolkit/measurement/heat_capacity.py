'''
This module define the [HeatCapacityMeasurment] instance,
which is a descendant of [Measurement].

Heat Capcity's experiment condition:
[field_strength]
'''

from .base import Measurement
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ppms_toolkit.sample import Sample  # Avoid Cylic-Import


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


from .utils import merge_by_temp_diff, debye_model_extended, debye_model

plt.rcParams['axes.grid'] = True  # Would like every plot to have grid


class HeatCapacityMeasurement(Measurement):
    def __init__(self,
                 filepath: str,
                 sample: "Sample",
                 sample_mass: float = 1,
                 field_strength: float = 0,
                 comment: str = "",
                 metadata=None
                 ):
        self.field_strength = field_strength
        self.sample_mass = sample_mass
        super().__init__(
            filepath=filepath, 
            sample=sample,
            comment= comment,
            metadata= metadata)
        if sample:  # If sample is inputted, add this mesurement in the sample.
            sample.add_measurement(self)

    def __repr__(self):
        return (f'HC exp, {self.sample_name} '
                f'with {self.field_strength} '
                f'Oe {self.comment}'
                f'T-range {self.t_range}'
                )
    
    def to_dict(self):
        '''Return a dict for representation purpose'''

        return {
                "External field": getattr(self, "field_strength", None),
                "Temp Range":     getattr(self, "t_range", None),
                "instance": self
        }

    def process_data(self, raw_df, filepath) -> pd.DataFrame:
        import re
        # Remove the comment lines.
        df = raw_df[raw_df['Comment ()'] == '']
        
        # Remove the error Code, fix the corrupted error code.
        # Keep columns as an Index so we can access the `.str` accessor.
        df.columns = df.columns.astype(str).str.replace('�', 'µ', regex=False)
        # Convert all str into Floats

        pattern = (     r'Time Stamp \(|'
                r'Samp HC \(|'
                r'Samp HC\/Temp \(|'
                r'Sample Temp \(|'
                r'Samp HC Err \(|'
                r'Field \('
                )


        # Use Index.str.contains directly on the columns Index.
        keys_to_keep = df.columns[df.columns.str.contains(pattern)]
        df = df[keys_to_keep]
        df = df.apply(pd.to_numeric, errors='coerce')
        
        df = merge_by_temp_diff(df=df,
                                temp_col='Sample Temp (Kelvin)',
                                tol=0.01)
        
        # Divide the Moment by sample_mass, if there's none 1 sample mass.
        pattern = re.compile(r'^(Samp HC \(|Samp HC/Temp \(|Samp HC Err \()')
        for col in df.columns:
            if pattern.match(col):
                df[col] = df[col] / self.sample_mass
        
        # Get the range of T
        minimum = df['Sample Temp (Kelvin)'].min()
        maximum = df['Sample Temp (Kelvin)'].max()
        self.t_range = f'{minimum:.1f} ~ {maximum:.1f}'

        return df

    def plot(self, ax=None):
        '''Create a standard plot of Heat Capacity Measurement'''
        if ax is None:
            fig, ax = plt.subplots(1, 2, figsize=(12, 4),dpi=300)

        cols = self.dataframe.columns
        sample_T = cols[cols.str.contains(r'Sample Temp \(')][0]
        sample_HC = cols[cols.str.contains(r'Samp HC \(')][0]
     
        # The first graph is a Samp HC v.s. T
        ax.plot(self.dataframe[sample_T],
                self.dataframe[sample_HC],
                label=f'{self.field_strength} Oe',)
        ax.set_xlabel(sample_T)
        ax.set_ylabel(sample_HC)
        ax.legend()

        return ax

    def background_subtraction(self,
                               mask_func=lambda T: T > 0,
                               model=debye_model, bounds=None, p0=None):
        from scipy.optimize import curve_fit

        T = self.dataframe['Sample Temp (Kelvin)']
        HC = self.dataframe['Samp HC (µJ/K)']

        mask = mask_func(T)
        T_fit = T[mask]
        HC_fit = HC[mask]

        kwargs = {}
        if bounds is not None:
            kwargs['bounds'] = bounds
        if p0 is not None:
            kwargs['p0'] = p0

        params, _ = curve_fit(model, T_fit, HC_fit, **kwargs)
        phonon_background = model(T, *params)
        subtracted = HC - phonon_background

        fig, ax = plt.subplots()

        ax.plot(T, HC, label='Heat Capacity')
        ax.plot(T, phonon_background, label='Phonon Background')
        ax.plot(T, subtracted, label='Subtracted.')
        plt.title(f'{self.sample_name} Phonon Background Subtraction')
        plt.legend()

        return fig, ax, params, T, subtracted

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
