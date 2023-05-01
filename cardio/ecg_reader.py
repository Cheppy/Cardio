"""""Signal reading factory"""
import os

import numpy as np
import pyedflib


class SignalFactory:
    @staticmethod
    def create_signal_reader(file_path):
        """
        Creates a SignalReader object based on the file type.
        """
        file_type = os.path.splitext(file_path)[-1]
        signal_reader_dict = {
            ".edf": EDFSignal,  # EDF, BDF
            ".DAT": BinaryCustom  # Chinese
        }

        if file_type in signal_reader_dict:
            return signal_reader_dict[file_type](file_path)
        else:
            raise ValueError(f"Unsupported file type. Try one of {set(signal_reader_dict.keys())}")


class Signal:
    def __new__(cls, file_path):
        return Signal.from_file(file_path)

    @classmethod
    def from_file(cls, file_path):
        reader = SignalFactory.create_signal_reader(file_path)
        entity = reader
        return entity


class SignalReader:
    def __init__(self, file_path):
        self.__file_path = file_path
        self._signals = None
        self.labels = None
        self.header = None
        self.n_signals = None
        self.times = None
        self.fs = None  # Frequency
        self.read_data(file_path)

    @property
    def signals_list(self):
        """"
        :return: list of signals available in ECG"
        """
        return self._signals

    def read_data(self, file_path):
        """
        Reads signal data from a file.
        """
        raise NotImplementedError

    def get_signal_by_index(self, signal_index, start=0, end=None):
        """
        Returns a single signal from the file based on the given index.
        """
        if self.signals_list is None:
            raise ValueError("No data loaded yet.")

        signal = self.signals_list[signal_index]
        return signal[start:end]

    def __repr__(self):
        return f"(FILE: {self.__file_path}, SIGNALS:{self.n_signals})"


class EDFSignal(SignalReader):
    def __init__(self, file_path):
        super().__init__(file_path)

    def read_data(self, file_path):
        """
        Reads signal data from an EDF file.
        """
        with pyedflib.EdfReader(file_path) as f:
            self.header = f.getHeader()
            self._signals = [f.readSignal(i) for i in range(f.signals_in_file)]
            self.labels = f.getSignalLabels()
            self.n_signals = f.signals_in_file
            self.fs = [f.getSampleFrequency(i) for i in range(f.signals_in_file)]


class BinaryCustom(SignalReader):
    """Reads .DAT files from Chinese database"""
    def read_data(self, file_path):
        """
        Reads signal data from a text file.
        """
        points_array = np.loadtxt(file_path)
        self._signals = [points_array[:, 1]]
        self.times = [points_array[:, 0]]
        self.labels = ["ECG"] * len(self.signals_list)
        # TODO TAY_FI.DAT EXAMPLE OF MORE SIGNALS NEEDED
        # IMPORTANT: .DAT Files could differ
        self.n_signals = 1


class CSVSignal(SignalReader):
    # TODO STRUCTURE NOT FOUND ATM
    def read_data(self, file_path):
        pass
