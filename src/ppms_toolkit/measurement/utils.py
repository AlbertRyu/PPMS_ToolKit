'''
This module provide some useful util functions
that might be used in general purpose
'''
import pandas as pd
import numpy as np
from scipy.integrate import quad

def merge_by_temp_diff(df,
                       temp_col='Sample Temp (Kelvin)',
                       tol=0.01):

    df_sorted = df.sort_values(by=temp_col).reset_index(drop=True)

    temp_diffs = df_sorted[temp_col].diff().abs()

    group_ids = (temp_diffs > tol).cumsum()

    merged_df = df_sorted.groupby(group_ids).mean(numeric_only=True)

    merged_df = merged_df.reset_index(drop=True)

    return merged_df

    '''
        df_sorted = df.sort_values(by=temp_col).reset_index(drop=True)

    groups = []
    current_group = [0]

    for i in range(1, len(df_sorted)):
        t_curr = df_sorted.loc[i, temp_col]
        t_prev = df_sorted.loc[current_group[-1], temp_col]
        if abs(t_curr - t_prev) < tol:
            current_group.append(i)
        else:
            groups.append(current_group)
            current_group = [i]
    groups.append(current_group)

    merged_rows = []
    for group in groups:
        averaged = df_sorted.loc[group].mean(numeric_only=True)
        merged_rows.append(averaged)
    
    '''


# Debye Model for Phonon
R = 8.314  # J/(mol·K)


def debye_integral(x):
    x = np.clip(x, 1e-10, 500)
    ex = np.exp(x)
    denom = (ex - 1)
    return np.where(denom == 0, 0, x**4 * ex / denom**2)


def debye_model(T, theta_D, scale=1.0):
    T = np.array(T)
    C = []

    for t in T:
        if t == 0:
            C.append(0.0)
        else:
            x_max = min(500, theta_D / t)
            integral, _ = quad(debye_integral, 0, x_max)
            c = 9 * R * (t / theta_D)**3 * integral * scale
            C.append(c)

    return np.array(C)


def einstein_model(T, theta_E, scale=1.0):
    x = theta_E / T
    return 3 * R * (x**2) * np.exp(x) / (np.exp(x) - 1)**2 * scale


def debye_model_extended(T, theta_D, B, D, scale=1.0):
    T = np.array(T)
    C = []

    for t in T:
        if t == 0:
            C.append(0.0)
        else:
            integral, _ = quad(debye_integral, 0, theta_D / t)
            c = 9 * R * (t / theta_D)**3 * integral * scale
            C.append(c)

    return np.array(C) + B * T + D


def gauss_with_step(x, A, x0, sigma, cL, cR):
    step = np.where(x < x0, cL, cR)
    return A * np.exp(-((x - x0)**2) / (2 * sigma**2)) + step

def gauss(x, A, x0, sigma, c):
    return A * np.exp(-(x-x0)**2/(2*sigma**2)) + c