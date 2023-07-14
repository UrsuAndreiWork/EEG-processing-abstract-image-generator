import os
import sys
import mne
import numpy as np
import scipy
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QThreadPool
from mne.preprocessing import ICA
from scipy.signal import welch
from WindowPictures import WindowPictures
from WindowAbstractImage import ImageWindow
from WindowGraph import WindowGraph
from Worker import Worker
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None
        self.w2 = None
        self.w3 = None
        self.threadpool = QThreadPool()
        self.setWindowTitle("App")
        self.buttonStart=QPushButton("Start scan")
        self.buttonGraph=QPushButton("View graph")
        self.buttonGenImage=QPushButton("Generate abstract image")
        self.buttonExit=QPushButton("Exit")
        self.buttonGradient="qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #555555, stop: 1 #222222);"

        pagelayout = QVBoxLayout()
        button_layout = QVBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(button_layout)
        pagelayout.addLayout(self.stacklayout)

        self.buttonStart.pressed.connect(self.activate_tab_1)
        self.buttonStart.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        button_layout.addWidget(self.buttonStart)

        self.buttonGraph.pressed.connect(self.activate_tab_2)
        self.buttonGraph.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        button_layout.addWidget(self.buttonGraph)

        self.buttonGenImage.pressed.connect(self.activate_tab_3)
        self.buttonGenImage.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        button_layout.addWidget(self.buttonGenImage)

        self.buttonExit.pressed.connect(self.activate_tab_4)
        self.buttonExit.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        button_layout.addWidget(self.buttonExit)

        button_layout.setSpacing(15)

        widget = QWidget()
        widget.setLayout(pagelayout)
        gradientBg = "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #87CEFA, stop: 1 white);"
        widget.setStyleSheet("background: "+gradientBg+"color: #333333; font: bold 14px;")
        self.setCentralWidget(widget)


    def progress_fn(self, n):
        print("%d%% done" % n)

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        self.buttonStart.setEnabled(True)
        self.buttonStart.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        print("THREAD COMPLETE!")


    def on_finished(self):
        self.w2.close()
        self.thread_finished = True


    def on_finised_abstract_image(self):
        self.thread_finished = True

    def thread_complete_abstract_image(self):
        print("THREAD COMPLETE!")

    def progress_fn_abstract_image(self, n):
        print("%d%% done" % n)

    def print_output_abstract_image(self, s):
        print(s)

    def closeEvent(self, event):
        # Execute function on close
        self.cleanup()
        event.accept()

    def cleanup(self):
        print("Cleaning up before closing.")
        # Perform any necessary cleanup before closing the app
        sys.exit(0)

    def selectFile(self, startPath):
        Tk().withdraw()
        default_path = startPath
        file_path_csv = askopenfilename(initialdir=default_path)
        return file_path_csv



    def calculatePSD(self,file_path_csv):
        eeg_data = np.genfromtxt(file_path_csv, delimiter=',', skip_header=8, usecols=(0, 1, 2, 3, 4, 5, 6,7))
        headers = ["FZ", "FC1", "FC2", "CP3", "CPZ", "CP4", "PZ","POZ"]
        window = np.hanning(512)
        nperseg = 512
        noverlap = 256
        nfft = 1024
        sampling_frequency = 250
        psd_values = {}
        # PSD pentru fiecare channel
        for i, header in enumerate(headers):
            freqs, psd = welch(eeg_data[:, i], fs=sampling_frequency, window=window, nperseg=nperseg, noverlap=noverlap,
                               nfft=nfft)
            psd_values[header] = psd
        return freqs,psd_values

    def calculatePSDWithIca(self, file_path_csv):

        eeg_data = np.genfromtxt(file_path_csv, delimiter=',', skip_header=8, usecols=(0, 1, 2, 3, 4, 5, 6, 7))
        headers = ["FZ", "FC1", "FC2", "CP3", "CPZ", "CP4", "PZ", "POZ"]
        sampling_frequency = 250
        window = np.hanning(512)
        nperseg = 512
        noverlap = 128
        nfft = 1024
        psd_values = {}

        channel_locations = {
            'FZ': [0, 1.8, 0],
            'FC1': [-0.7, 1.3, 0],
            'FC2': [0.7, 1.3, 0],
            'CP3': [-1.3, -1, 0],
            'CPZ': [0, -1, 0],
            'CP4': [1.3, -1, 0],
            'PZ': [0, -1.8, 0],
            'POZ': [0, -2.2, 0]
        }

        montage = mne.channels.make_dig_montage(
            channel_locations, coord_frame="head", nasion=[0, 1, 0], lpa=[-1, 0, 0], rpa=[1, 0, 0]
        )

        # Creating the RawArray
        info = mne.create_info(ch_names=headers, sfreq=sampling_frequency, ch_types="eeg")
        raw = mne.io.RawArray(eeg_data.T, info)
        raw.set_montage(montage)

        # Filtering the data
        raw.filter(l_freq=0.5, h_freq=60)

        ica = ICA(n_components=3, method='infomax', random_state=0)
        ica.fit(raw)

        # Get the kurtosis of each ICA component
        kurtosis = scipy.stats.kurtosis(ica.get_sources(raw).get_data(), axis=1)

        # Set a threshold for the kurtosis
        kurtosis_threshold = 5  # This is an example value; you may need to adjust this based on your specific data

        print("Kurtosis values:", kurtosis)
        # Exclude components whose kurtosis exceeds the threshold
        ica.exclude = np.where(kurtosis > kurtosis_threshold)[0]

        # Apply the ICA to the raw data, excluding the chosen components
        raw_clean = ica.apply(raw.copy(), exclude=ica.exclude)

        # PSD for each channel
        for i, header in enumerate(headers):
            freqs, psd = welch(raw_clean.get_data()[i, :], fs=sampling_frequency, window=window, nperseg=nperseg,
                               noverlap=noverlap, nfft=nfft)
            psd_values[header] = psd
        return freqs, psd_values

    def activate_tab_1(self):
        if self.w2 is None:
            self.w2 = WindowPictures()
            self.w2.addPictures()
        self.w2.actualPicture = 0
        self.buttonStart.setEnabled(False)
        disableButtonGradient = "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #000000, stop: 1 #222222);"
        self.buttonStart.setStyleSheet("background: " + disableButtonGradient + "color: white; font: bold 14px;")

        # self.w2.changePicture(False)

        worker = Worker(self.w2.changePicture)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.finished.connect(self.on_finished)
        self.threadpool.start(worker)

        # t = th.Timer(0.001, self.w2.changePicture, args=(False,))
        # t.start()
        self.w2.show()

    def activate_tab_2(self):
        file_path_csv = self.selectFile('resources/headset data')
        if file_path_csv!='':
            freqs, psd_values = self.calculatePSD(file_path_csv)
            freqsIca, psd_valuesIca = self.calculatePSDWithIca(file_path_csv)
            print(freqsIca,psd_valuesIca)
            if self.w is None:
                self.w = WindowGraph(freqs, psd_values, freqsIca, psd_valuesIca)
            self.w.show()
            self.w=None

    def on_w3_closed(self):
        self.w3 = None

    def showWindow(self):
        self.buttonGenImage.setEnabled(True)
        self.buttonGenImage.setStyleSheet("background: " + self.buttonGradient + "color: white; font: bold 14px;")
        self.buttonGenImage.setText("Generate abstract image")
        self.w3.displayWindow()

    def activate_tab_3(self):
        file_path_csv = self.selectFile('resources/headset data')
        print(file_path_csv)
        if file_path_csv!='':
            self.buttonGenImage.setEnabled(False)
            disableButtonGradient = "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #000000, stop: 1 #222222);"
            self.buttonGenImage.setStyleSheet("background: " + disableButtonGradient + "color: white; font: bold 14px;")
            self.buttonGenImage.setText("Loading...")

            freqs, psd_values = self.calculatePSD(file_path_csv)
            psd_array = np.array(list(psd_values.values()))

            if self.w3 is None:
                self.w3 = ImageWindow(psd_values,psd_array,freqs, os.path.basename(file_path_csv))
                self.w3.showWindowSignal.connect(self.showWindow)
                self.w3.window_closed.connect(self.on_w3_closed)

            def start_generating_wrapper(progress_callback):
                self.w3.startGenerating(progress_callback)

            worker = Worker(start_generating_wrapper)
            worker.signals.result.connect(self.print_output_abstract_image)
            worker.signals.finished.connect(self.on_finised_abstract_image)
            worker.signals.progress.connect(self.progress_fn_abstract_image)

            self.threadpool.start(worker)

    def activate_tab_4(self):
        sys.exit(0)
