import pyedflib


class EDFReader:
    def __init__(self, edf_path):
        self.edf_path = edf_path
        self.n_signals = None
        self.labels = None
        self.signals = None
        self.header = None
        self.read_edf()

    def read_edf(self):
        """
        :return:
        """
        # Open the EDF file
        with pyedflib.EdfReader(self.edf_path) as f:
            self.header = f.getHeader()
            self.n_signals = f.signals_in_file
            self.__signals = [f.readSignal(i) for i in range(self.n_signals)]
            self.labels = f.getSignalLabels()

    @property
    def signals_list(self):
        return self.__signals

    def get_signal_by_index(self, signal_index, start=0, end=None):
        #TODO IDEAS :  start and as list [start, end] for readability
        """
              Returns a single signal from the EDF file based on the given index.
              :param signal_index: The index of the signal to retrieve.
              :param start: The starting index of the signal data to retrieve. if not filled - starts from beginning
              :param end: The ending index of the signal data to retrieve.
              :return: A numpy array containing the signal data.
        """
        if signal_index < self.n_signals:
            return self.__signals[signal_index][start:end]
        else:
            raise ValueError(f"Signal index out of range. Number of signals in the file: {self.n_signals}")




