# PPMS Data Processing Kit

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/AlbertRyu/PPMS_ToolKit/HEAD?urlpath=%2Fdoc%2Ftree%2Fexamples%2Fcode_example.ipynb)

A lightweight Python toolkit for extracting, processing, and analyzing data from the **Physical Property Measurement System (PPMS)**.

## Usage

This light weight Python toolkit should helps you:

- 📂 **Transform** raw PPMS `.dat` files into convenient `NumPy` arrays or `pandas` DataFrames
- 📈 **Visualize** experimental data quickly
- 🧮 **Process** data, e.g., phonon background subtraction
- 📊 **Fit** data to extract physical parameters (e.g., Curie temperature)

## Data Structure

This kit essentially contains two object: Sample and Measurements

### 🧪 `Sample`

- Stores basic sample metadata: `name`, `mass`, `creation_time`, etc.
- Maintains a list of associated measurements.
- You can:
  - Create a sample independently.
  - Add measurements to it later.

### 📊 `Measurement`

- Represents a single experimental dataset.
- Can exist independently or be assigned to a `Sample`.
- Provides tools specific to the measurement type (e.g., heat capacity analysis).

#### Supported Measurement Types

```text
Measurement
├── HeatCapacityMeasurement
└── MagnetismMeasurement
    ├── MT (Magnetization vs Temperature)
    └── MH (Magnetization vs Field)
```

## 💾 Save and Load

After parsing and processing your raw .dat file and entering experimental metadata (e.g., sample name, mass),
you can save the current state of a Sample (including all measurements) using Python’s built-in pickle. For example. 

```python
ImportantSample = Sample(id=1, name="Mn-PEA", mass=1.88)
ImportantSample.add_Measurement(some_measurement)

ImportantSample.save()
```
A `.pkl` file contains all information and measurement of the sample with be created in the current directory. Next time, simply run

```python
ImportantSampleFromTimeAgo = Sample.load('Mn-PEA')
```

This allows you to reload fully processed samples without needing to re-run the initial parsing or metadata input.

## 🛠️ Installation Guide

This document explains how to clone, install, and use the `ppms_toolkit` package locally.

#### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/AlbertRyu/PPMS_ToolKit.git

cd PPMS_ToolKit
```

#### 2. (Optional, Recommended) Create and Use in a Virtual Environment

We recommend using a virtual environment to isolate dependencies:use Anaconda, venv or anything you like.

#### 3. Install the Package in Development Mode

```bash
pip install -e .
```

#### 4. You can now import the packages in Python. E.g, 🥳

```python
from ppms_toolkit.sample import Sample
from ppms_toolkit.measurement import HeatCapacityMeasurement
```

## 📦 Dependencies

This package relies on beloved libraries
`numpy` ,`pandas`, `scipy` and `matplotlib`.
