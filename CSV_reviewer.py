import sys
import pandas as pd
import numpy as np
import argparse
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton
import pyqtgraph as pg

class TimeSeriesViewer(QtWidgets.QWidget):
    def __init__(self, csv_path):
        super().__init__()

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.setWindowTitle("Time Series Viewer")
        self.resize(1400, 800)

        # === Load CSV ===
        self.data = pd.read_csv(csv_path)
        self.columns = self.data.columns.tolist()
        self.time = self.data[self.columns[0]].values
        self.y_data = {col: self.data[col].values for col in self.columns[1:]}
        self.selected_columns = [self.columns[1]]
        self.max_points = 6000
        self.peak_ratio_threshold = 10
        self.plots = {}

        # === Plot area ===
        self.canvas = pg.GraphicsLayoutWidget()

        # === Right control panel ===
        self.selector = QtWidgets.QListWidget()
        self.selector.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.selector.addItems(self.columns[1:])
        self.selector.itemSelectionChanged.connect(self.on_column_changed)

        self.save_btn = QPushButton("Save Image as PNG")
        self.save_btn.clicked.connect(self.save_plot)

        self.jump_input = QLineEdit()
        self.jump_input.setPlaceholderText("Jump to time (s)")
        self.jump_btn = QPushButton("Jump")
        self.jump_btn.clicked.connect(self.jump_to_time)

        self.range_start = QLineEdit()
        self.range_start.setPlaceholderText("Start time")
        self.range_end = QLineEdit()
        self.range_end.setPlaceholderText("End time")
        self.range_btn = QPushButton("Set Range")
        self.range_btn.clicked.connect(self.set_time_range)

        self.reset_btn = QPushButton("Reset View")
        self.reset_btn.clicked.connect(self.reset_view)

        # === Layouts ===
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Select Channels:"))
        right_panel.addWidget(self.selector, stretch=2)  # ✅ auto-stretch selector
        right_panel.addSpacing(10)
        right_panel.addWidget(self.save_btn)
        right_panel.addSpacing(10)
        right_panel.addWidget(QLabel("Jump to Time:"))
        right_panel.addWidget(self.jump_input)
        right_panel.addWidget(self.jump_btn)
        right_panel.addSpacing(10)
        right_panel.addWidget(QLabel("Display Range:"))
        right_panel.addWidget(self.range_start)
        right_panel.addWidget(QLabel("to"))
        right_panel.addWidget(self.range_end)
        right_panel.addWidget(self.range_btn)
        right_panel.addSpacing(10)
        right_panel.addWidget(self.reset_btn)
        right_panel.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.canvas, stretch=4)
        right_container = QtWidgets.QWidget()
        right_container.setLayout(right_panel)
        right_container.setFixedWidth(250)
        main_layout.addWidget(right_container)

        self.setLayout(main_layout)

        for i in range(self.selector.count()):
            item = self.selector.item(i)
            if item.text() == self.selected_columns[0]:
                item.setSelected(True)

        self.init_plots()

    def on_column_changed(self):
        self.selected_columns = [item.text() for item in self.selector.selectedItems()]
        self.init_plots()

    def init_plots(self):
        self.canvas.clear()
        self.plots.clear()

        if not self.selected_columns:
            return

        peaks = [np.ptp(self.y_data[col]) for col in self.selected_columns]
        multi_plot = max(peaks) / (min(peaks) + 1e-6) > self.peak_ratio_threshold

        if multi_plot:
            x_link_plot = None
            for idx, col in enumerate(self.selected_columns):
                plot = self.canvas.addPlot(row=idx, col=0)
                plot.setLabel('left', col)
                plot.setMouseEnabled(x=True, y=False)
                if x_link_plot is None:
                    x_link_plot = plot
                    plot.setLabel('bottom', self.columns[0], units='s')
                else:
                    plot.setXLink(x_link_plot)

                pen = pg.mkPen(color=pg.intColor(idx), width=2.5)
                curve = pg.PlotDataItem(pen=pen, name=col)
                plot.addItem(curve)
                self.plots[col] = (plot, curve)
                plot.sigXRangeChanged.connect(self.update_all)
        else:
            plot = self.canvas.addPlot(row=0, col=0)
            plot.setLabel('bottom', self.columns[0], units='s')
            plot.setMouseEnabled(x=True, y=False)
            plot.addLegend()
            for idx, col in enumerate(self.selected_columns):
                pen = pg.mkPen(color=pg.intColor(idx), width=2.5)
                curve = pg.PlotDataItem(pen=pen, name=col)
                plot.addItem(curve)
                self.plots[col] = (plot, curve)
            plot.sigXRangeChanged.connect(self.update_all)

        self.update_all()

    def update_all(self):
        for col, (plot, curve) in self.plots.items():
            x = self.time
            y = self.y_data[col]

            # Current window range for drawing (still use downsample)
            x_min, x_max = plot.viewRange()[0]
            mask = (x >= x_min) & (x <= x_max)
            indices = np.nonzero(mask)[0]

            if len(indices) > self.max_points:
                step = len(indices) // self.max_points
                indices = indices[::step]

            x_plot = x[indices]
            y_plot = y[indices]
            curve.setData(x_plot, y_plot)

            # ✅ Set Y axis range based on entire signal, not local window
            full_y = y
            y_min = full_y.min()
            y_max = full_y.max()
            margin = 0.05 * (y_max - y_min) if y_max > y_min else 1.0
            plot.setYRange(y_min - margin, y_max + margin, padding=0)

    def save_plot(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save image", "", "PNG files (*.png)")
        if file_path:
            exporter = pg.exporters.ImageExporter(self.canvas.scene().items()[0])
            exporter.export(file_path)

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Right):
            for plot, _ in self.plots.values():
                x_min, x_max = plot.viewRange()[0]
                shift = 0.1 * (x_max - x_min)
                if event.key() == QtCore.Qt.Key_Left:
                    new_min = x_min - shift
                    new_max = x_max - shift
                else:
                    new_min = x_min + shift
                    new_max = x_max + shift
                plot.setXRange(new_min, new_max, padding=0)

    def jump_to_time(self):
        try:
            t = float(self.jump_input.text())
            window_width = 2.0
            for plot, _ in self.plots.values():
                plot.setXRange(t - window_width / 2, t + window_width / 2, padding=0)
        except ValueError:
            pass

    def set_time_range(self):
        try:
            t1 = float(self.range_start.text())
            t2 = float(self.range_end.text())
            if t2 > t1:
                for plot, _ in self.plots.values():
                    plot.setXRange(t1, t2, padding=0)
        except ValueError:
            pass

    def reset_view(self):
        full_start, full_end = self.time[0], self.time[-1]
        for plot, _ in self.plots.values():
            plot.setXRange(full_start, full_end, padding=0)

# === Command line entry ===

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", nargs="?", default="C:\\Users\\hsiangxu\\Documents\\data\\0417\\MBLUEankle_0417.csv", help="Path to CSV file")
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    viewer = TimeSeriesViewer(args.csv)
    viewer.show()
    sys.exit(app.exec_())

