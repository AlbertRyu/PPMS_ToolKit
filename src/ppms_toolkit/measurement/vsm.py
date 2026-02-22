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

from .utils import gauss

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
                #"orientation":getattr(self, "sample_orientation", None),
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
        
    def plot(self, mid=None, ax=None, susceptibility=True, legend: str|list = 'Exp Setting' ):

        if ax is None:
            fig, ax = plt.subplots()

        label: str|None = None
        if legend == 'Exp Setting':
            if self.mode == 'MH':
                label = f'{mid if mid else ''} {self.const_temp:.0f}K' 
            elif self.mode == "MT":
                label = f'{self.const_field}Oe {self.condition} {self.sample.orientation or "Unknown Ori"} {mid if mid else ''}' 
        elif legend == 'Sample Name':
            label = f'{self.sample.name}'
        elif type(legend) is list:
            label = " ".join(str(getattr(self, l)) for l in legend)
        else:
            raise ValueError("Legend Mode is not set")


        df = self.dataframe

        regex = '^Moment'
        ax.set_ylabel('Moment (emu / gram)')
        if self.mode == 'MT':
            if susceptibility:
                regex = 'chi'
                ax.set_ylabel('Susceptibility (emu)')
            ax.plot(df.filter(regex='^Temperature'), df.filter(regex=regex).squeeze(), label = label)
            ax.set_xlabel('Temperature(K)')
        elif self.mode == 'MH':
            ax.plot(df.filter(regex='Magnetic Field'), df.filter(regex=regex).squeeze(), label = label)
            ax.set_xlabel('Magnetic Field(Oe)')
        else:
            print('Ah oh, something went wrong. Check if measurement.mode is "MH" or "MT".')
        
        #ax.set_ylabel('Susceptibility (emu)')
        ax.set_title(f'{self.sample.name} {self.mode} {self.sample.orientation if self.sample.orientation else ''}')
        ax.legend()

        return ax


    def fit_MH(self, fit_window = [0,70000], window_length=101, p0=None):
        """
        from M(H) curve, do dM/dH gussian fit, to extract:
        - x0_fit: Peak Position (Oe)
        - FWHM : Full Width Half Maximum (Oe)
        also return fig, ax
        """

        fig, ax = plt.subplots(1,2, figsize=(16,5))

        df = self.dataframe

        field_col = "Magnetic Field (Oe)"
        moment_col = "Moment (emu)"

        mask_field = (df[field_col] > fit_window[0]) & (df[field_col] < fit_window[1])
        this_df = df.loc[mask_field].copy()

        if this_df.empty:
            raise ValueError("fit_MH: No datapoint in desired fit_window")

        # Transform into Numpy Array
        ExtField = this_df[field_col].to_numpy()
        Moment   = this_df[moment_col].to_numpy()

        dMdH = np.gradient(Moment, ExtField)

        dMdH_detrended = detrend(dMdH)
        base_y = dMdH - dMdH_detrended

        if window_length >= len(dMdH_detrended):
            # 选一个最大可能的奇数窗
            window_length = max(3, len(dMdH_detrended) // 2 * 2 + 1)
        dMdH_detrended_filtered = savgol_filter(dMdH_detrended, window_length, polyorder=3)

        mask = (dMdH > 0) & (10000 < ExtField)
        x_fit = ExtField[mask]
        y_fit = dMdH_detrended_filtered[mask]

        # 3) 给出初始猜测 p0
        if p0 is None:
            A0     = y_fit.max() - y_fit.min()    # 峰高
            max_idx = int(np.argmax(y_fit))
            x00    = float(x_fit[max_idx])      # 峰位
            sigma0 = (x_fit.max() - x_fit.min())/6  # 大致半宽
            c0     = y_fit.min()                   # 底线
            p0 = [A0, x00, sigma0, c0]

        # 4) 拟合
        popt, pcov = curve_fit(gauss, x_fit, y_fit, p0=p0)
        A_fit, x0_fit, sigma_fit, c_fit = popt
        sigma_fit = abs(sigma_fit)
        FWHM = 2 * np.sqrt(2 * np.log(2)) * sigma_fit

        ax[0].scatter(ExtField, dMdH_detrended_filtered, s=1, label= 'Detrended Filtered Data')
        ax[0].plot(ExtField, gauss(ExtField, *popt), '-', lw=2, label='Guassian fit',color='g')
        ax[0].axvline(x0_fit, color='r', ls='--', label=f'Peak @ {x0_fit:.0f} Oe, FWHM = {FWHM}')
        ax[0].legend()
        
        ax[1].scatter(ExtField, dMdH, s=1, label = 'OG Data')
        ax[1].plot(ExtField, gauss(ExtField, *popt)+base_y, '-', lw=2, label='Guassian fit',color='r')
        ax[1].legend()
        
        fig.suptitle(f'dMdH, T = {self.const_temp}')

        return x0_fit, FWHM, fig, ax
        


    def fit_MT(self, 
               fit_func, 
               fit_window:list, 
               p0=None,
               detrended:bool = True,
               smooth_window:int = 101,
               deriv_smooth_window:int = 31
               ):

        field = self.const_field
        this_df = self.dataframe
        
        chi = this_df['chi']
        Temp = this_df['Temperature (K)']

        # --- 1. 等间距插值 & 平滑 χ(T) -----------------------------------
        f_interp = interp1d(
            Temp,
            chi,
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate")# type: ignore[arg-type]

        # 生成等间距 T_new
        T_new = np.linspace(np.min(Temp), np.max(Temp), 2000)
        chi_resampled = f_interp(T_new)

        # 窗口必须是奇数且 < 数据长度
        smooth_window = min(smooth_window, len(T_new) // 2 * 2 + 1)
        chi_smooth = savgol_filter(chi_resampled, window_length=smooth_window, polyorder=3)

        # Take gradient
        dchidT = np.gradient(chi_smooth, T_new)

        mask = np.isfinite(dchidT) 
        dchidT_clean = dchidT[mask]
        T_new_clean = T_new[mask]

        # --- 3. 去趋势 & 再平滑 -------------------------------------------
        if detrended:
            dchidT_trend_removed = detrend(dchidT_clean)
        else:
            dchidT_trend_removed = dchidT_clean.copy()

        base_y = dchidT_clean - dchidT_trend_removed
        deriv_smooth_window = min(deriv_smooth_window,
                              len(dchidT_trend_removed) // 2 * 2 + 1)
        dchidT_detrended_filtered = savgol_filter(dchidT_trend_removed, deriv_smooth_window, 3)

        
        left, right = fit_window
        mask = (T_new_clean > left) & (T_new_clean<right)
        x_fit = T_new_clean[mask]
        y_fit = dchidT_detrended_filtered[mask]

            # --- 5. 初始猜测 p0（如果未给） -----------------------------------
        if p0 is None:
            A0 = float(y_fit.max() - y_fit.min())
            # 粗略峰位：拟合区内最大值
            x00 = float(x_fit[np.argmax(y_fit)])
            sigma0 = float((x_fit.max() - x_fit.min()) / 6)
            c0 = float(y_fit.min())
            p0 = [A0, x00, sigma0, c0]

        # 4) 拟合
        popt, pcov = curve_fit(fit_func, x_fit, y_fit, p0=p0)

        A_fit, x0_fit, sigma_fit, c_fit = popt

        FWHM = 2 * np.sqrt(2 * np.log(2)) * sigma_fit

        # 5) 作图验证
        fig, ax = plt.subplots(1,2,figsize=(12,5))

        ax[0].plot(T_new_clean, dchidT_detrended_filtered, '.', ms=3, alpha=0.5, label='data')
        ax[0].plot(x_fit, y_fit, '.', ms=5, label='fit region')
        ax[0].plot(T_new_clean, fit_func(T_new_clean, *popt), '-', lw=2, label='Guassian fit')
        ax[0].axvline(x0_fit, color='r', ls='--', label=f'Peak @ {x0_fit:.2f} T, FWHM = {FWHM:.3f}')
        ax[0].set_title(f'Field = {field} Oe')
        ax[0].set_xlabel('Temperature(K)')
        ax[0].set_ylabel('dChidT (emu/K)')
        ax[0].legend()

        ax[1].scatter(T_new_clean, dchidT_clean,s=1, label='original')
        ax[1].plot(T_new_clean, base_y, label='linear background')
        ax[1].scatter(T_new_clean,dchidT_trend_removed, label='Detrended',s=1)
        ax[1].scatter(T_new_clean,dchidT_detrended_filtered, label='Detrended+Filtered',s=1)
        ax[1].set_xlabel('Temperature (K)')
        ax[1].set_ylabel('dchi/dT (emu/K)')
        ax[1].legend()

        plt.grid(True, linestyle='--', alpha=0.6, which='major') 

        return fig, ax, x0_fit, FWHM

    
