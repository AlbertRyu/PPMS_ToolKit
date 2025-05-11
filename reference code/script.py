
''' This module is for fitting and plot the desired graph. '''

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.optimize import curve_fit  # noqa: E402
from scipy.signal import savgol_filter
from scipy.interpolate import CubicSpline
from matplotlib.ticker import ScalarFormatter
from IPython.display import set_matplotlib_formats


from currie_weiss_law import curie_weiss_law, curie_weiss_law_inverse, \
                             mod_curie_weiss_law
from data_processing import get_paths, dat_2_dataframe

# This cell recorded the molar mass of mentioned material might be used.
MOLAR_MASS = {
    'MN': 54.938,
    'CU': 63.546
}

# Some parameter should be assigned manually
# before plot for each different material.
SAMPLE_MASS = 15
SAMPLE_MOLE = 1
FOLDER = 'PLEASE DEFINE'
# In order that I don't need to write the name of the materials every time.
# Every materials is put in a folder with the name of the material.
FILE_NAMES = ['FILENAME_1', 'FILENAME_2']

'''
Different kinds of currie Weiss Law
t = Temperature
c = Curie Constant
t_c = Curie_Weiß Temperature
'''


def get_data_dic(filenames, SAMPLE_MOLE, folder, mode):
    '''
    Always first Retrive the Data Dictionary

    Mode: 'T' for M-T, 'H' for M-H curve.

    '''
    paths = get_paths(filenames, folder)
    return dat_2_dataframe(paths, SAMPLE_MOLE, mode)


def plot(df_dic: dict, mode='T',
         x_range=0, y_range=0, x_range_inv=0, y_range_inv=0):
    '''
    This function plot receives the dictionary of Data.
    And plot their Moment (emu) out
    '''

    if mode == 'T':
        fig, ax = plt.subplots(1, 1, figsize=(6, 5))
        # !! This line changed on 12/12/2024,
        # makes the chi_inverse plot disappear.
        target_x = 'Temperature (K)'
        target_y1 = 'Magnetisation (emu / gram)'
    elif mode == 'H':
        fig, ax = plt.subplots(1, 1, figsize=(6, 5))
        target_x = 'Magnetic Field (Tesla)'
        target_y1 = 'Moment (emu / gram)'

    for filename in df_dic:
        data = df_dic[filename]
        if mode == 'T':
            sns.lineplot(x=target_x, y=target_y1,
                         data=data, ax=ax, label=filename)
            # sns.lineplot(x=target_x, y='chi_Invese',
            #            data=data, ax=ax[1], label=filename)
        elif mode == 'H':
            sns.lineplot(x=target_x, y=target_y1,
                         data=data, ax=ax, label=filename)

        # if x_range and y_range parameters is used. Using them instead.
        if x_range != 0:
            ax.set_xlim(x_range)
        if y_range != 0:
            ax.set_ylim(y_range)
        '''
        if y_range_inv != 0:
            ax[1].set_ylim(y_range_inv)
        if x_range_inv != 0:
            ax[1].set_xlim(x_range_inv)
        '''
        # fig.legend(loc='upper right')
        # Style the plot
        ax.grid(linewidth=0.5)
        ax.tick_params(axis='both', which='major', labelsize=13)
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    set_matplotlib_formats("retina")
    plt.tight_layout()

    return fig, ax


def prepare_fit_data(filename, data_dic, start=3, end=300):

    '''Cut the data, and return the fit data as a list'''

    data = data_dic[filename]

    sigma = data['M. Std. Err. (emu)']

    # Make sure that temperature is descending.
    data = data.sort_values(by='Temperature (K)', ascending=False)

    T = data['Temperature (K)'].to_numpy()  # Temperatures
    chi = data['Magnetisation (emu / gram)']  # Susceptibility measurements

    start_index = T[T < start].size
    end_index = T[T > end].size

    def cutted_data(column):
        cutted_column = column[end_index:-start_index]
        return cutted_column
    fit_data = [T, chi, sigma, cutted_data(T),
                cutted_data(chi), cutted_data(sigma)]

    return fit_data


def fit_cw(fit_data, initial_guess=15, inversed=True,
           including_sigma=True):

    '''This function fit the desired Data and return the fitted parameter'''

    T, chi, sigma, T_fit, chi_fit, sigma_fit = fit_data

    if inversed:
        chi = 1 / chi
        fit_data[1] = chi
        chi_fit = 1 / chi_fit
        fit_data[4] = chi_fit
        law = curie_weiss_law_inverse
    else:
        law = curie_weiss_law

    if including_sigma:
        popt, pcov, *remaining = \
            curve_fit(law, T_fit, chi_fit, p0=[1, initial_guess],
                      sigma=sigma_fit)
    else:
        popt, pcov, *remaining = curve_fit(law, T_fit, chi_fit,
                                           p0=[1, initial_guess])
    chi_pred = law(T_fit, *popt)
    return popt, pcov, chi_pred


def fit_mod_cw(fit_data, initial_guess=[0, 1], including_sigma=True):

    '''This function fit the desired Data and return the fitted parameter'''

    T, chi, sigma, T_fit, chi_fit, sigma_fit = fit_data

    law = mod_curie_weiss_law

    if including_sigma:
        popt, pcov, *remaining = \
            curve_fit(law, T_fit, chi_fit, p0=[1, *initial_guess],
                      sigma=sigma_fit)
    else:
        popt, pcov, *remaining = curve_fit(law, T_fit, chi_fit,
                                           p0=[1, *initial_guess])

    chi_pred = law(T_fit, *popt)
    return popt, pcov, chi_pred


def plot_fitted_line(fit_data, chi_pred, ax):
    '''The Function pot the fitted data'''

    T, chi, sigma, T_fit, chi_fit, sigma_fit = fit_data

    # Plot the data and the fit
    ax.scatter(T, chi, color='red', s=1, label='Experimental data')
    ax.plot(T_fit, chi_pred, label='Fitted Line', color='blue')

    ax.set_xlabel('Temperature (K)')
    ax.set_ylabel('Magnetic Susceptibility')
    ax.legend()

    return ax


def get_CW_T_and_Curie_Constant(MT_data, field='0P01T',
                                mode='FC', orientation='IP', start=150):
    name = f'{field}_{mode}_{orientation}'
    fit_data = prepare_fit_data(name, MT_data, start=start, end=300)
    popt, pcov, chi_pred = fit_cw(fit_data)

    fig, ax = plt.subplots()
    plot_fitted_line(fit_data, chi_pred, ax)
    ax.set_title(f"Currie_Weiss Tc= {popt[1]:.2f}")
    return popt[1], popt[0]


def cal_mu_eff(Curie_Constant):
    'Calculate the effective magnetic moment from Curie Constant'
    kb = 1.38064852E-23  # Boltzmann constant
    NA = 6.02214076E23
    mu_B = 9.274009994E-24
    return np.sqrt(3 * Curie_Constant * kb / (NA * mu_B ** 2))


# The function below is for the M-H curve analyzing.
# get2derivative retrives the Hsp, while the extract_MR_and_Hc
# retrives the MR and Hc.


def get2derivative(y, x, window_length=81, polyorder=3):
    dy_dx = np.gradient(y, x)

    dy_dx_smooth = savgol_filter(dy_dx, window_length, polyorder)
    d2y_dx2 = np.gradient(dy_dx_smooth, x)
    d2y_dx2_smooth = savgol_filter(d2y_dx2, window_length, polyorder)

    fig, ax = plt.subplots(1, 3, figsize=(16, 4))

    ax[0].plot(x, y)
    ax[0].set_title('M(H)')
    ax[1].plot(x, dy_dx_smooth)
    ax[1].set_title('dM_dH')
    ax[2].plot(x, d2y_dx2_smooth)
    ax[2].set_title('d2M_dH2')

    return fig, ax


def extract_MR_and_Hc(fields, moments):

    cs = CubicSpline(x=fields[::-1][1:], y=moments[::-1][1:])
    MR = cs(0).tolist() * 10000
    print(f'The MR is extract by Cubic Spines: {MR:.4f}')

    test_x = np.linspace(-0.1, 0.1, 20000)
    test_y = np.array([cs(x).tolist() for x in test_x])
    Hc = test_x[abs(test_y).argmin()] * 10000
    print(f'The Hc is extract by Cubic Spines: {Hc:.4f} Oe')
    
    x_s = np.linspace(-7, 7, 10000)
    Moments_interp = [cs(x) for x in x_s]
    Moments_interp = np.array([x.tolist() for x in Moments_interp])

    fig, ax = plt.subplots()
    ax.plot(x_s, Moments_interp)
    ax.set_title('M(H)')
    ax.set_xlim(-0.005, 0.005)
    ax.set_ylim(-1E-4, 1E-4)
    ax.vlines(x=0, ymin=-1E-4, ymax=1E-4, linestyles='dashed', color='r')
    ax.hlines(y=0, xmin=-0.02, xmax=0.02, linestyles='dashed', color='r')
    ax.vlines(x=Hc/10000, ymin=-1E-4, ymax=1E-4,
              linestyles='dashed', color='g', label=f'Hc = {Hc:.2f} Oe')
    ax.hlines(y=MR/10000, xmin=-0.02, xmax=0.02,
              linestyles='dashed', color='y', label=f'MR = {MR:.2f} Oe')
    plt.legend()

    return fig, ax
