from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QGridLayout, QWidget
import pyqtgraph as pg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

class PlotWidgetICA(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.canvas.draw()

class PyQtGraphWidgetICA(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.plotIca = pg.PlotWidget(title="PSD of every channel after ICA")
        self.plotIca.setLabel('bottom', 'Frequency (Hz)')
        self.plotIca.setLabel('left', 'PSD (dB/Hz)')
        self.plotIca.showGrid(x=True, y=True)
        self.legend = self.plotIca.addLegend(offset=(-10, 30))

        layout = QVBoxLayout()
        layout.addWidget(self.plotIca)
        self.setLayout(layout)

class PyQtGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.plot = pg.PlotWidget(title="PSD of every channel")
        self.plot.setLabel('bottom', 'Frequency (Hz)')
        self.plot.setLabel('left', 'PSD (dB/Hz)')
        self.plot.showGrid(x=True, y=True)
        self.legend = self.plot.addLegend(offset=(-10, 30))

        layout = QVBoxLayout()
        layout.addWidget(self.plot)
        self.setLayout(layout)

class WindowGraph(QMainWindow):
    def __init__(self, freqs, psd_values, freqsIca, psd_valuesIca):
        super().__init__()
        self.resize(1250, 700)
        df = pd.DataFrame(psd_values, index=freqs)
        average_psd = df.mean(axis=1)

        dfIca = pd.DataFrame(psd_valuesIca, index=freqsIca)
        average_psdIca = dfIca.mean(axis=1)

        self.setWindowTitle('Plots of EEG')

        plot_widget = PlotWidget()
        plot_widget.ax.set_title("Average PSD of All Channels")
        plot_widget.ax.semilogy(average_psd.index, average_psd.values)
        plot_widget.ax.set_xlabel('Frequency (Hz)')
        plot_widget.ax.set_ylabel('PSD (dB/Hz)')
        plot_widget.ax.grid(True)
        plot_widget.figure.tight_layout()
        plot_widget.canvas.draw()

        plot_widget2 = PlotWidgetICA()
        plot_widget2.ax.set_title("Average PSD of All Channels After ICA")
        plot_widget2.ax.semilogy(average_psdIca.index, average_psdIca.values)
        plot_widget2.ax.set_xlabel('Frequency (Hz)')
        plot_widget2.ax.set_ylabel('PSD (dB/Hz)')
        plot_widget2.ax.grid(True)
        plot_widget2.figure.tight_layout()
        plot_widget2.canvas.draw()

        pyqtgraph_widget = PyQtGraphWidget()
        pyqtgraph_widget.plot.plot(freqs, psd_values["FZ"], pen=(255, 0, 0), name="FZ")
        pyqtgraph_widget.plot.plot(freqs, psd_values["FC1"], pen=(0, 255, 0), name="FC1")
        pyqtgraph_widget.plot.plot(freqs, psd_values["FC2"], pen=(125, 0, 125), name="FC2")
        pyqtgraph_widget.plot.plot(freqs, psd_values["CP3"], pen=(125, 125, 0), name="CP3")
        pyqtgraph_widget.plot.plot(freqs, psd_values["CP4"], pen=(0, 125, 125), name="CP4")
        pyqtgraph_widget.plot.plot(freqs, psd_values["PZ"], pen=(125, 125, 125), name="PZ")
        pyqtgraph_widget.plot.plot(freqs, psd_values["POZ"], pen=(205, 75, 10), name="POZ")

        pyqtgraph_widget_ica = PyQtGraphWidgetICA()
        pyqtgraph_widget_ica.plotIca.plot(freqsIca, psd_valuesIca["FZ"], pen=(255, 0, 0), name="FZ")
        pyqtgraph_widget_ica.plotIca.plot(freqsIca, psd_valuesIca["FC1"], pen=(0, 255, 0), name="FC1")
        pyqtgraph_widget_ica.plotIca.plot(freqsIca, psd_valuesIca["FC2"], pen=(125, 0, 125), name="FC2")
        pyqtgraph_widget_ica.plotIca.plot(freqsIca, psd_valuesIca["CP3"], pen=(125, 125, 0), name="CP3")
        pyqtgraph_widget_ica.plotIca.plot(freqsIca, psd_valuesIca["CPZ"], pen=(0, 125, 125), name="CPZ")
        pyqtgraph_widget_ica.plotIca.plot(freqsIca, psd_valuesIca["CP4"], pen=(0, 0, 255), name="CP4")
        pyqtgraph_widget_ica.plotIca.plot(freqs, psd_values["PZ"], pen=(125, 125, 125), name="PZ")
        pyqtgraph_widget_ica.plotIca.plot(freqs, psd_values["POZ"], pen=(205, 75, 10), name="POZ")

        central_widget = QWidget()
        central_layout = QGridLayout()
        central_layout.addWidget(plot_widget, 0, 0)
        central_layout.addWidget(plot_widget2, 1, 0)
        central_layout.addWidget(pyqtgraph_widget, 0, 1)
        central_layout.addWidget(pyqtgraph_widget_ica, 1, 1)
        central_widget.setLayout(central_layout)

        self.setCentralWidget(central_widget)
        self.show()