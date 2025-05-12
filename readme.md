# PPMS Data Processing Kit

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

