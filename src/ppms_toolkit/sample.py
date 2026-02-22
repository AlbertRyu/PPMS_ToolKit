'''

'''

import pickle
import os
from datetime import date
from multiprocessing import Pool, set_start_method

import pandas as pd
from IPython.display import display, Markdown
import matplotlib.pyplot as plt

from .measurement import Measurement,VSMMeasurement,HeatCapacityMeasurement


class Sample:
    '''
    This modules defined each sample, their properties
    and their supported functions.

    The Samples should contains serveal Measurement and could
    be save into a .pickel file and reload some time again.


    Parameters
    ----------
    name : str
        Name of the sample.
    id   : float, optional
        Assign a unique id to the sample.
    orientation : str
        either "In Plane" or "Out of Plane"
    mass : float, optional
        Mass of the sample, unit is mg.
    make_date: str
        make date of the sample, in "%Y-%m-%d" format.

    Attributes
    ----------
    measurements: list
        a list of measurements assigned to this sample.
     All the parameters.
    '''
    def __init__(self, name: str,
                 id: float | None = None,
                 orientation: str | None = None,
                 mass: float | None = None,
                 make_date: str | None = None):
        self.name = name
        self.orientation = orientation
        self.id = id
        self.mass = mass  # milligram
        self.make_date = \
            date.fromisoformat(make_date) if make_date else None
        self._measurements = []

    @property
    def measurements(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        '''Represent the measurement list as dataframes'''
        df_vsm = self.measurements_vsm
        df_hc = self.measurements_hc
        return df_vsm, df_hc
    
    @property
    def show_measurements(self):
        df_vsm = self.measurements_vsm
        df_hc = self.measurements_hc
        if df_hc.empty:
            print("There's no HC measurements bind to this sample.")
        else:
            display(Markdown("#### HeatCapacity Measurements List"))
            display(df_hc)

        if df_vsm.empty:
            print("There's no VSM measurements bind to this sample.")
        else:
            display(Markdown("#### VSM Measurements List"))
            display(df_vsm)
        
    @property
    def measurements_vsm(self):
        return self.get_measurements_vsm()

    def get_measurements_vsm(self, mode=None):
        '''Represent the measurement list as pd.Dataframe'''

        measurements = (
            m for m in self._measurements
            if isinstance(m, VSMMeasurement)
            and (mode is None or m.mode == mode)
        )
        df = pd.DataFrame(m.to_dict() for m in measurements)

        if df.empty:
            return df

        # 决定排序规则
        sort_key = 'const temp' if mode == 'MH' else 'const field'

        return df.sort_values(sort_key)

    @property
    def measurements_hc(self):
        '''Represent the measurement list as pd.Dataframe'''
        hc_rows = []
        for m in self._measurements:
            if isinstance(m, HeatCapacityMeasurement):
                hc_rows.append(m.to_dict())
        df_hc =pd.DataFrame(hc_rows)
        return df_hc
        
    def set_make_date(self, make_date: str):
        self.make_date = date.fromisoformat(make_date)

    def add_measurement(self, m: Measurement):
        if m not in self._measurements:
            print(f'{m} (added)')
            self._measurements.append(m)
            m.sample = self  # double-linked with the measurement
        else:
            print(f'The Measurment [{m}] \n'
                  f'is already exist in sample [{self}] ')

    def save(self):
        with open(f'{self.name}'
                  f'({self.make_date if self.make_date else "Unknown MakeTime"}).pkl', "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)

    def _vsm_measurement_reader(self, args):

        path, orientation = args
        if 'MT' in path:
            mode =  'MT'
        elif 'MH' in path:
            mode =  'MH'
        else:
            raise ValueError(f'Mode is not contained in filename of {path}')
    
        m=VSMMeasurement(filepath=path, 
                         sample=self, 
                         mode=mode)

        return m


    def add_vsm_measurements_by_folder(self, folder_path, paralelle=False):

        """
        bind multiple vsm measurement by folder name
        """
        if os.name != "posix":
            set_start_method("spawn", force=True)

        if 'IP' in folder_path:
            orientation = "In Plane"
        elif 'OOP' in folder_path:
            orientation = "Out of Plane"
        else:
            raise ValueError(f'Orientation is not contained in folderpath {folder_path}')
        
        arg_list = [(folder_path + p, orientation) for p in os.listdir(folder_path)]

        if paralelle:
            with Pool() as pool: 
                measurements = pool.map(self._vsm_measurement_reader, arg_list)

            for m in measurements:
                self.add_measurement(m)
        else:
            for args in arg_list:
                m = self._vsm_measurement_reader(args)
                self.add_measurement(m)


    def __repr__(self):
        date = self.make_date if self.make_date else "Unknwon Date"
        return (f'id: {self.id}, '
                f'{self.name}, '
                f'{self.mass}mg, '
                f'made in {date}.')
    

    ## This function is not quite useful.
    def plot_vsm(self, mode, ax=None, field=None, temperature=None, condition=None, susceptibility=True, legend: str|list='Exp Setting'):

        if not ax:
            fig ,ax = plt.subplots()

        df = self.measurements_vsm
        if mode=='MH':
            df = self.measurements_vsm.sort_values('const temp')

        if mode:
            mask_mode = df['mode'] == mode
        else:
            mask_mode = True
        
        if field:
            mask_field = df['const field'] == field
        else:
            mask_field = True
        
        if temperature:
            mask_temp = df['const temp'] == temperature
        else:
            mask_temp = True


        df_filtered = df[mask_field & mask_mode & mask_temp]
        for index, row in df_filtered.iterrows():
                if condition:
                    if row['instance'].condition == condition:
                        row['instance'].plot(ax=ax, susceptibility=susceptibility, legend=legend)
                else:
                        row['instance'].plot(ax=ax, susceptibility=susceptibility, legend=legend)

