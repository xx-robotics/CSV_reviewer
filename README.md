# 📈 Time Series Viewer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)  
[![PyQt5](https://img.shields.io/badge/PyQt5-Compatible-green.svg)](https://pypi.org/project/PyQt5/)  
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

A lightweight and fast Python GUI tool for visualizing large time-series data from CSV files.  
Built with **PyQt5** and **pyqtgraph** for smooth interaction and high performance.

---

## 🔧 Features

- Multi-channel time series viewer
- Intelligent downsampling for large datasets
- Auto multi-subplot layout when value ranges differ significantly
- Scroll to zoom and drag to pan (X-axis only)
- Keyboard arrow keys to pan quickly
- Jump to specific timestamp
- View any custom time range
- Export current view as PNG
- Responsive layout with right-side control panel
- Command-line support for loading CSV

---

## 🚀 Usage

```bash
python viewer.py your_data.csv
```

- The first column in the CSV should be **Time**
- Subsequent columns are treated as individual data channels

---

## ⌨️ Controls

- **Mouse scroll**: Zoom X-axis
- **Mouse drag**: Pan X-axis
- **← / →**: Shift view left/right
- **Jump to time**: Center view on input timestamp
- **Set range**: Zoom into a specified time interval
- **Reset view**: Return to full data range
- **Save image**: Export current view as PNG

---

## 📦 Requirements

Install dependencies with:

```bash
pip install pandas pyqt5 pyqtgraph
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
