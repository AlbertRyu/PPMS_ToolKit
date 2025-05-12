'''
This module provide some useful util functions
that might be used in general purpose
'''
import pandas as pd


def merge_by_temp_diff(df,
                       temp_col='Puck Temp (Kelvin)',
                       tol=0.01):
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

    return pd.DataFrame(merged_rows)
