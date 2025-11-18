'''
This module define the [VSM_Measurement] instance,
which is a descendant of [Measurement].

VSM experiment condition:
[Sample Orientation]
'''

from .base import Measurement
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, detrend
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d #,PchipInterpolator,UnivariateSpline
from .utils import gauss_with_step, gauss

if TYPE_CHECKING:
    from ppms_toolkit.sample import Sample  # Avoid Cylic-Import


class VSMMeasurement(Measurement):
    def __init__(self,
                    mode: str,
                    sample: 'Sample',
                    filepath: str | None = None,
                    raw_dataframe: pd.DataFrame | None = None,  # 新增
                    processed_dataframe: pd.DataFrame | None = None,  # 新增
                    comment: str = "",
                    metadata: dict | None =None
                 ):
        self.mode = mode
        self.const_temp = None
        self.const_field = None
        self.condition = None
        super().__init__(
            filepath=filepath, 
            sample=sample, 
            comment=comment, 
            metadata=metadata,
            raw_dataframe=raw_dataframe,
            processed_dataframe=processed_dataframe)
        
        if metadata:
            self.const_field = metadata.get('const_field')
            self.const_temp = metadata.get('const_temp') or metadata.get('const_temperature')
            self.condition = metadata.get('condition') 

        sample.add_measurement(self)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in ("MH", "MT"):
            raise ValueError("Mode can only be 'MH' or 'MT'")
        self._mode = value

    def to_dict(self):
        '''Return a dict for representation purpose'''
        return {
                "mode":      getattr(self, "mode", None),
                "orientation":getattr(self, "sample_orientation", None),
                "const temp": getattr(self, "const_temp", None),
                "const field": getattr(self, "const_field", None),
                "instance": self
        }
    
    def process_data(self, raw_df, filepath) -> pd.DataFrame:      
        import re

        pattern = (     
                r'^Temperature \(|'
                r'Magnetic Field \(|'
                r'Moment \(|'
                r'M. Std. Err. \('
                )
     
        cols = raw_df.columns
        keys_to_keep = cols[cols.str.contains(pattern)]
        df = raw_df[keys_to_keep].apply(pd.to_numeric, errors='coerce')


        # Divide the Moment by, if there's none 1 sample mass.
        for col in df.columns:
            if re.match(r'Moment',col):
                df[col] = df[col] / self.sample.mass

        if self.mode == 'MT':
            self.const_field = np.average(df.filter(regex='Magnetic Field')).round().astype(int)
            for col in df.columns:
                if re.match(r'Moment',col):
                    df['chi'] = df[col] / self.const_field
            if re.search(r'ZFC', filepath):
                self.condition = 'ZFC'
            elif re.search(r'FC', filepath):
                self.condition = 'FC'
            else:
                self.condition = 'Unknown Condition'

        else:
            self.const_temp = np.average(df.filter(regex='^Temperature')).round(1)

        return df
    
    
    def __repr__(self):
        if self.mode == 'MT':
            return (f'{self.mode} on {self.sample_name} '
                    f'with {self.sample.orientation or "Unknown"} orientation '
                    f'at {self.const_field}Oe')
        else:
            return (f'{self.mode} on {self.sample_name} '
                    f'with {self.sample.orientation or "Unknown"} orientation '
                    f'at {self.const_temp}K')
        
    def plot(self, mid=None, ax=None, susceptibility=True, legend = 'Sample Name' ):

        if ax is None:
            fig, ax = plt.subplots(dpi=300)

        if legend == 'Exp Setting':
            label = f'{mid}-{self.const_field}Oe - {self.condition} - {self.sample.orientation or "Unknown Ori"}' 
        elif legend == 'Sample Name':
            label = f'{self.sample.name}'

        if susceptibility:
            regex = 'chi'
            ax.set_ylabel('Susceptibility (emu)')
        else:
            regex = '^Moment'
            ax.set_ylabel('Moment (emu / gram)')

        df = self.dataframe
        print(type(df.filter(regex='chi').squeeze()))

        if self.mode == 'MT':
            ax.plot(df.filter(regex='^Temperature'), df.filter(regex=regex).squeeze(), label = label)
            ax.set_xlabel('Temperature(K)')
        elif self.mode == 'MH':
            ax.plot(df.filter(regex='Magnetic Field'), df.filter(regex=regex).squeeze(), label = label)
            ax.set_xlabel('Magnetic Field(Oe)')
        else:
            print('Ah oh, something went wrong. Check if measurement.mode is "MH" or "MT".')
        
        ax.set_ylabel('Susceptibility (emu)')
        #ax.set_title(f'{self.mode} - {self.sample_name}')

        ax.legend()

        return ax

    '''
    def get_df_by_field(df, field):
        m = df[df['const field'] == field]['instance'].values[0]
        df = m.dataframe.sort_values('Temperature (K)')
        return df
    '''

    def fit_MH(self):
        fig, ax = plt.subplots(1,2, figsize=(16,5))

        mask1 = self.dataframe['Magnetic Field (Oe)'] < 70000
        mask2 = self.dataframe['Magnetic Field (Oe)'] > 0
        this_df = self.dataframe[mask1 & mask2]

        Moment = this_df['Moment (emu)']
        ExtField = this_df['Magnetic Field (Oe)']

        dMdH = np.gradient(Moment, ExtField)

        dMdH_detrended = detrend(dMdH)
        base_y = dMdH - dMdH_detrended
        dMdH_detrended_filtered = savgol_filter(dMdH_detrended, 101, 3)

        mask = (dMdH > 0) & (10000 < ExtField)
        x_fit = ExtField[mask]
        y_fit = dMdH_detrended_filtered[mask]

        # 3) 给出初始猜测 p0
        A0     = y_fit.max() - y_fit.min()    # 峰高
        x00    = x_fit.iloc[np.argmax(y_fit)]      # 峰位
        sigma0 = (x_fit.max() - x_fit.min())/6  # 大致半宽
        c0     = y_fit.min()                   # 底线
        p0 = [A0, x00, sigma0, c0]

        # 4) 拟合
        popt, pcov = curve_fit(gauss, x_fit, y_fit, p0=p0)
        A_fit, x0_fit, sigma_fit, c_fit = popt

        ax[0].scatter(ExtField, dMdH_detrended_filtered, s=1, label= 'Detrended Filtered Data')
        ax[0].plot(ExtField, gauss(ExtField, *popt), '-', lw=2, label='Guassian fit',color='g')
        ax[0].axvline(x0_fit, color='r', ls='--', label=f'Peak @ {x0_fit:.0f} Oe, FWHM = {2 * np.sqrt(2 * np.log(2)) * sigma_fit:.0f}')
        ax[0].legend()
        
        ax[1].scatter(ExtField, dMdH, s=1, label = 'OG Data')
        ax[1].plot(ExtField, gauss(ExtField, *popt)+base_y, '-', lw=2, label='Guassian fit',color='r')
        ax[1].legend()
        
        fig.suptitle(f'dMdH, T = {self.const_temp}')

        return fig, ax
        


    def fit_MT(self, left, right, peak_pos):
        field = self.const_field
        this_df = self.dataframe
        
        chi = this_df['chi']
        Temp = this_df['Temperature (K)']

        f_interp = interp1d(Temp, chi, kind='linear', bounds_error=False, fill_value="extrapolate") # type: ignore[arg-type]
        # 生成等间距 T_new
        T_new = np.linspace(np.min(Temp), np.max(Temp), 2000)
        chi_resampled = f_interp(T_new)
        chi_resampled_smooth = savgol_filter(chi_resampled, window_length=21, polyorder=3)


        dchidT = np.gradient(chi_resampled_smooth, T_new)

        mask = np.isfinite(dchidT) 
        dchidT_clean = dchidT[mask]
        T_new_clean = T_new[mask]
        
        # dchidT_clean = dchidT_clean[mask]
        # T_new_clean = T_new_clean[mask]

        dchidT_detrended = detrend(dchidT_clean)

        base_y = dchidT_clean - dchidT_detrended
        dchidT_detrended_filtered = savgol_filter(dchidT_detrended, 31, 3)
        
        mask = (T_new_clean > left) & (T_new_clean<right)
        x_fit = T_new_clean[mask]
        y_fit = dchidT_detrended_filtered[mask]

        # 3) 给出初始猜测 p0
        A0     = y_fit.max() - y_fit.min()    # 峰高
        x00    = peak_pos     # 峰位
        sigma0 = (x_fit.max() - x_fit.min())/6  # 大致半宽
        sigma1 = (x_fit.max() - x_fit.min())/6
        c0     = y_fit.min()                   # 底线
        p0 = [A0, x00, sigma0, sigma1, c0]

        # 4) 拟合
        popt, pcov = curve_fit(gauss_with_step, x_fit, y_fit, p0=p0)

        A_fit, x0_fit, sigma_fit, sigma_R, c_fit = popt

        FWHM = 2 * np.sqrt(2 * np.log(2)) * sigma_fit


        # 5) 作图验证
        fig, ax = plt.subplots(1,2,figsize=(12,5))
        ax[0].plot(T_new_clean, dchidT_detrended_filtered, '.', ms=3, alpha=0.5, label='data')
        ax[0].plot(x_fit, y_fit, '.', ms=5, label='fit region')
        ax[0].plot(T_new_clean, gauss_with_step(T_new_clean, *popt), '-', lw=2, label='Guassian fit')
        ax[0].axvline(x0_fit, color='r', ls='--', label=f'Peak @ {x0_fit:.2f} T, FWHM = {FWHM:.3f}')
        ax[0].set_title(f'Field = {field} Oe')
        ax[0].set_xlabel('Temperature(K)')
        ax[0].set_ylabel('dChidT (emu/K)')
        ax[0].legend()

        ax[1].scatter(T_new_clean, dchidT_clean,s=1, label='original')
        ax[1].plot(T_new_clean, base_y, label='linear background')
        ax[1].scatter(T_new_clean,dchidT_detrended, label='Detrended',s=1)
        ax[1].scatter(T_new_clean,dchidT_detrended_filtered, label='Detrended+Filtered',s=1)
        ax[1].set_xlabel('Temperature (K)')
        ax[1].set_ylabel('dchi/dT (emu/K)')
        ax[1].legend()

        plt.grid(True, linestyle='--', alpha=0.6, which='major') 

        return fig, ax, x0_fit, FWHM

    
