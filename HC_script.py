# This module contains useable functions
# related to heat capacity data processing.

import pandas as pd
import matplotlib.pyplot as plt


def readDataFile(file_path):
    # 读取整个文件，检查数据部分
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        content = file.readlines()

    # 找到数据部分的起始行
    data_start = None
    for i, line in enumerate(content):
        if line.strip() == "[Data]":
            data_start = i + 1  # 数据部分从 [Data] 下一行开始
            break

    # 读取数据部分
    if data_start is not None:
        data_lines = content[data_start:]

        # 尝试解析数据列
        data = [line.strip().split(",")
                for line in data_lines if line.strip()]

        # 将数据转换为 DataFrame
        df = pd.DataFrame(data)

        # 尝试解析第一行作为列名
        df.columns = df.iloc[0]  # 第一行作为列名
        df = df[1:].reset_index(drop=True)  # 移除原来的列名行

        # 尝试将数值列转换为浮点数
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                pass  # 不是数值的列跳过

    else:
        df = None  # 数据未找到
        print("未找到 [Data] 标记，无法解析数据部分。")

    return df


def dfProcess(df, file_path):
    # 1. remove rows with NaN
    # 2. remove useless columns

    reduced_df = df[['Puck Temp (Kelvin)', 'System Temp (Kelvin)',
                    'Sample Temp (Kelvin)', 'Temp Rise (Kelvin)']].copy()

    try:
        reduced_df['Samp HC (J/mole-K)'] = df['Samp HC (J/mole-K)']
    except KeyError:
        print(f"No HC(J/mole-K) for {file_path}. Get Sample HC(J/K) instead.")
        reduced_df['Samp HC (J/K)'] = df['Samp HC (J/K)']

    reduced_df['T2'] = reduced_df['Sample Temp (Kelvin)'] ** 2
    reduced_df['C/T'] = \
        reduced_df['Samp HC (J/K)']/reduced_df['Sample Temp (Kelvin)']

    reduced_df = reduced_df.dropna()
    return reduced_df


def genDataDictionary(file_paths):
    data_dic = {}
    for file_path in file_paths:
        df = readDataFile(file_path)
        df = dfProcess(df, file_path)
        data_dic[file_path] = df
    return data_dic


def plotDataDictionary(data_dic):

    fig, ax = plt.subplots()

    for file_path, df in data_dic.items():
        y_axis = df.columns[df.columns.str.contains(r'^Samp HC')].values[0]
        ax.plot(df['Sample Temp (Kelvin)'],
                df[y_axis], label=file_path)

    ax.set_xlabel('Temperature (K)')
    ax.set_ylabel(y_axis)
    ax.legend()

    return fig, ax


def dicSelect(dic, keysToKeep):
    return {key: dic[key] for key in keysToKeep if key in dic}
