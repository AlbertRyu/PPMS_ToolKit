''' This module record all the of evaluate function used in ploting. '''
import numpy as np


def get_pred_dof_residue(law, T_fit, chi_fit, popt):
    ''' Return chi_pred and residue.'''

    chi_pred = law(T_fit, *popt)
    dof = len(T_fit) - len(popt)  # degree fo freedom

    return chi_pred, dof


def get_chi2_stat(chi_fit, chi_pred, dof):

    '''
    return chi2 and reduced_chi2.

    Definition of chi_sqaured:

    chi^2 = sum_i ( O_i - E_i )^2 / sigma_i^2

    O_i : The original value of i-th datapoint.
    E_i : The expected value of i-th datapoint.
    sigma_i : The standard deviation of the i_th datapoint.
    sigma_i^2 : variance of i-th datapoint.

    reduced_chi^2 = chi^2 / dof
    with dof = number of datapoints - number of fitting parameters.

    '''
    chi2_stat = np.sum((chi_fit - chi_pred) ** 2 / (chi_pred))
    reduced_chi2 = chi2_stat / dof

    return chi2_stat, reduced_chi2


def get_r2_stat(chi_fit, chi_pred, dof):
    ''' get r squared stats. '''
    ss_res = np.sum((chi_pred - chi_fit)**2)  # sum of squares of residuals
    ss_tot = np.sum((chi_fit - np.mean(chi_fit))**2)  # Total sum of squares
    r_squared = 1 - (ss_res / ss_tot)
    reduced_r_squared = 1 - (ss_res/(dof-1))/(ss_tot/(len(chi_fit)-1))
    return r_squared, reduced_r_squared


def evaluate(law, T_fit, chi_fit, popt, pcov):
    ''' Evaluate the quality of fit by chi_squared and r_squared'''

    c, t_c = popt
    dc, dt_c = np.sqrt(np.diag(pcov))

    chi_pred, dof = get_pred_dof_residue(law, T_fit, chi_fit, popt)

    chi2, reduced_chi2 = get_chi2_stat(chi_fit, chi_pred, dof)
    r_squared, reduced_r_squared = get_r2_stat(chi_fit, chi_pred, dof)

    # Print the results
    print(f"""
        Fitted Curie constant: C = {c:.5f} ± {dc:.8f}"
        Fitted Curie Weiß temperature: T_C = {t_c:.5f} ± {dt_c:8f}

        Chi_Squared: {chi2:.5f}
        Reduced Chi_Sqaured: {reduced_chi2:.5f}

        R Sqaured = {r_squared:.3f}
        Reduced R Sqaured = {reduced_r_squared:.3f}
        """)
