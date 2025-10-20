# PPMS Toolkit

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython/)

*A comprehensive Python toolkit for PPMS (Physical Property Measurement System) data analysis*

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Screenshots](#-screenshots)

</div>

---

## 📖 Overview

**PPMS Toolkit** is a modern, user-friendly application designed for researchers working with Quantum Design's Physical Property Measurement System (PPMS). It provides both a powerful **GUI application** and a flexible **Python library** for:

- 📂 **Data Management**: Import, organize, and manage PPMS `.dat` files with SQLite database
- 📊 **Interactive Plotting**: Visualize VSM and Heat Capacity measurements with Matplotlib
- 🔬 **Advanced Analysis**: Curie temperature fitting, background subtraction, susceptibility analysis
- 💾 **Efficient Storage**: Parquet-based file format for fast data loading and minimal disk usage
- 🎨 **Modern GUI**: Built with PySide6 (Qt6) for cross-platform compatibility

---

## ✨ Features

### 🖥️ GUI Application

- **Sample Management**
  - Create and edit sample metadata (name, mass, orientation, chemical formula)
  - Track multiple measurements per sample
  - Delete samples and associated data files

- **Measurement Management**
  - Batch import of `.dat` files from PPMS
  - Support for VSM (Vibrating Sample Magnetometer) measurements:
    - **MH mode**: Magnetization vs. Field
    - **MT mode**: Magnetization vs. Temperature
  - Support for Heat Capacity measurements
  - Automatic deduplication based on file content hash

- **Interactive Plotting**
  - Plot multiple measurements with customizable legends
  - Click-to-hide curves for easy comparison
  - Switch between susceptibility (χ) and moment views
  - Zoom, pan, and export plots

- **Data Filtering**
  - Multi-column filtering in measurement tables
  - Filter by sample, mode, field, temperature, or condition

### 🐍 Python Library

```python
from ppms_toolkit.sample import Sample
from ppms_toolkit.measurement import VSMMeasurement, HeatCapacityMeasurement

# Create a sample
sample = Sample(name="Fe3O4", mass=2.5, orientation="IP")

# Load VSM measurement
vsm = VSMMeasurement(
    filepath="path/to/data.dat",
    sample=sample,
    mode="MT"
)

# Plot and analyze
vsm.plot()
fig, ax, Tc, FWHM = vsm.fit_MT(left=290, right=310, peak_pos=300)

# Heat capacity analysis
hc = HeatCapacityMeasurement(
    filepath="path/to/hc.dat",
    sample=sample,
    field_strength=1000
)
fig, ax, params = hc.background_subtraction_debye()
```

---

## 🚀 Installation

### Option 1: Conda Environment (Recommended)

```bash
# Clone the repository
git clone https://github.com/AlbertRyu/PPMS_ToolKit.git
cd PPMS_ToolKit

# Create and activate conda environment
conda env create -f environment.yml
conda activate ppms_toolkit

# Install the package in development mode
pip install -e ".[gui]"

# Launch the GUI
ppms-toolkit
```

### Option 2: pip + venv

```bash
# Clone the repository
git clone https://github.com/AlbertRyu/PPMS_ToolKit.git
cd PPMS_ToolKit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with GUI support
pip install -e ".[gui]"

# Launch the GUI
ppms-toolkit
```

### Option 3: Library Only (No GUI)

```bash
pip install -e .
```

---

## 🎯 Quick Start

### GUI Workflow

1. **Launch Application**
   ```bash
   ppms-toolkit
   ```

2. **Select/Create Project**
   - Choose an existing project folder or create a new one
   - All data will be stored in this folder

3. **Add Samples**
   - Navigate to "Samples" tab
   - Click "Add Sample" and enter metadata (name, mass, orientation)

4. **Import Measurements**
   - Go to "Plots" tab
   - Click "Add Measurement"
   - Select multiple `.dat` files (batch import supported)
   - Choose the sample and measurement mode (MH/MT)

5. **Visualize Data**
   - Select measurements from the table
   - Click "Plot" to visualize
   - Use legend to toggle curves
   - Toggle χ/Moment view with checkbox

### Python Library Example

```python
from ppms_toolkit.sample import Sample
from ppms_toolkit.measurement import VSMMeasurement

# Create sample
sample = Sample(
    name="Mn-PEA",
    mass=1.88,  # mg
    orientation="IP",
    chemical="(C6H5CH2CH2NH3)2MnCl4"
)

# Load VSM measurement
vsm = VSMMeasurement(
    filepath="data/MT_100Oe.dat",
    sample=sample,
    mode="MT",
    comment="Field cooling"
)

# Quick plot
vsm.plot()

# Fit Curie temperature
fig, ax, Tc, FWHM = vsm.fit_MT(
    left=285,      # Left boundary of fitting region
    right=295,     # Right boundary
    peak_pos=290   # Initial guess for peak
)
print(f"Curie Temperature: {Tc:.2f} K")
print(f"FWHM: {FWHM:.3f} K")
```

---

## 📊 Supported Measurement Types

### VSM (Vibrating Sample Magnetometer)

| Mode | Description | Analysis Tools |
|------|-------------|----------------|
| **MH** | Magnetization vs. Field | `fit_MH()` - Coercivity extraction |
| **MT** | Magnetization vs. Temperature | `fit_MT()` - Curie temperature fitting |

**Features:**
- Automatic susceptibility calculation (χ = M/H)
- Gaussian fitting for phase transitions
- Background subtraction and detrending

### Heat Capacity

| Feature | Description |
|---------|-------------|
| **Background Subtraction** | Debye/Einstein model fitting |
| **Phonon Contribution** | Remove lattice contributions |
| **Temperature Range** | Automatic range detection |

**Available Models:**
- `debye_model`: Simple Debye model
- `debye_model_extended`: Multi-component Debye + constant
- `einstein_model`: Einstein oscillator model

---

## 🗂️ Project Structure

```
PPMS_ToolKit/
├── src/
│   ├── ppms_toolkit/              # Core library
│   │   ├── sample.py              # Sample class
│   │   └── measurement/
│   │       ├── base.py            # Base Measurement class
│   │       ├── vsm.py             # VSM analysis
│   │       └── heat_capacity.py   # Heat Capacity analysis
│   │
│   ├── ppms_toolkit_gui/          # GUI application
│   │   ├── app.py                 # Entry point
│   │   ├── main_window.py         # Main window
│   │   ├── controller/            # MVC controllers
│   │   ├── widgets/               # Qt widgets
│   │   └── dialogs/               # Dialog windows
│   │
│   └── infrastructure/
│       └── db/
│           └── db.py              # SQLite database wrapper
│
├── examples/
│   └── code_example.ipynb         # Jupyter notebook examples
│
├── pyproject.toml                 # Project metadata & dependencies
├── environment.yml                # Conda environment specification
└── README.md                      # This file
```

---

## 🔧 Dependencies

### Core Dependencies
- **numpy** ≥ 1.21 - Numerical computing
- **pandas** ≥ 1.3 - Data manipulation
- **scipy** ≥ 1.7 - Scientific computing
- **matplotlib** ≥ 3.4 - Plotting

### GUI Dependencies (Optional)
- **PySide6** ≥ 6.4 - Qt6 GUI framework
- **pyarrow** ≥ 10.0 - Parquet file I/O

### Development Dependencies
- **ipykernel** - Jupyter notebook support
- **IPython** - Enhanced interactive shell

---

## 📚 Documentation

### Key Classes

#### `Sample`
Represents a physical sample with metadata and associated measurements.

```python
sample = Sample(
    name="Sample1",
    mass=2.5,           # mg
    orientation="IP",   # In-plane or "OOP" (out-of-plane)
    chemical="Fe3O4"
)
```

#### `VSMMeasurement`
VSM measurement with analysis tools.

```python
vsm = VSMMeasurement(
    filepath="data.dat",
    sample=sample,
    mode="MT",           # "MT" or "MH"
    comment="Field cooling"
)

# Analysis methods
vsm.plot()                                    # Plot χ vs T/H
vsm.plot_magnetisation()                      # Plot M vs T/H
fig, ax, Tc, FWHM = vsm.fit_MT(285, 295, 290) # Fit Curie temp
fig, ax = vsm.fit_MH()                        # Fit coercivity
```

#### `HeatCapacityMeasurement`
Heat capacity measurement with background subtraction.

```python
hc = HeatCapacityMeasurement(
    filepath="hc.dat",
    sample=sample,
    field_strength=1000  # Oe
)

# Background subtraction
fig, ax, params = hc.background_subtraction_debye(
    mask_func=lambda T: (T > 5) & (T < 50)
)
```

### Database Structure

The toolkit uses SQLite for data management with two main tables:

**`samples`**
- `id`, `name`, `mass`, `chemical`, `orientation`, `created_at`, `notes`

**`measurements`**
- `id`, `sample_id` (FK), `measurement_type`, `mode`
- `const_field`, `const_temperature`
- `original_filepath`, `data_filepath`, `processed_data_filepath`
- `content_hash` (for deduplication)
- `extra_parameters` (JSON), `comment`, `created_at`

---

## 🖼️ Screenshots

### Main Window
*Sample management and measurement plotting interface*

### Interactive Plotting
*Click legend items to show/hide curves*

### Batch Import
*Import multiple .dat files at once*

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone and install in development mode
git clone https://github.com/AlbertRyu/PPMS_ToolKit.git
cd PPMS_ToolKit
pip install -e ".[gui]"

# Run tests (if available)
pytest tests/
```

---

## 📄 License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this software, provided that:
- You include the original copyright notice and license text in any copies
- You do not hold the author liable for any damages

See [LICENSE](LICENSE) file for full details.

---

## 👤 Author

**Yunxiao LIU**
- Email: yunxiao.liu@tum.de
- GitHub: [@AlbertRyu](https://github.com/AlbertRyu)

---

## 🙏 Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python)
- Data storage powered by [Apache Arrow](https://arrow.apache.org/) (Parquet format)
- Scientific computing with [NumPy](https://numpy.org/), [SciPy](https://scipy.org/), and [pandas](https://pandas.pydata.org/)

---

## 📝 Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{liu2025ppms,
  author = {Liu, Yunxiao},
  title = {PPMS Toolkit: A Python Toolkit for PPMS Data Analysis},
  year = {2025},
  url = {https://github.com/AlbertRyu/PPMS_ToolKit}
}
```

---

<div align="center">

**[⬆ Back to Top](#ppms-toolkit)**

Made with ❤️ for the research community

</div>
