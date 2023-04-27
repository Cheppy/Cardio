import unittest

import numpy

from utils.ecg_reader import Signal, BinaryCustom, EDFSignal


class TestSignal(unittest.TestCase):

    def test_bad_data_signal(self):
        """test the data that is written incorrectly, or bad decoded"""
        with self.assertRaises((UnicodeDecodeError, ValueError, OSError)):
            signal = Signal("test/data/bad_data.DAT")

        with self.assertRaises((OSError, UnicodeDecodeError, ValueError)):
            signal = Signal("test/data/bad_data.edf")

    def test_signal_reader(self):

        """Tests signal reader and correct file type"""
        # Test that the __signalreader method returns the correct SignalReader subclass
        signal = Signal("test/data/r01.edf")
        self.assertIsInstance(signal, EDFSignal)

        signal = Signal("test/data/TAY_FI.DAT")
        self.assertIsInstance(signal, BinaryCustom)

        with self.assertRaises(ValueError):
            signal = Signal("example.txt")

    def test_edf_signal(self):
        # Test that the EDFSignal class reads data correctly
        edf = EDFSignal("test/data/r01.edf")
        self.assertEqual(edf.n_signals, 5)
        self.assertEqual(edf.fs[0], 1000.0)
        self.assertEqual(edf.fs[1], 1000.0)
        self.assertEqual(len(edf.signals_list[0]), 300000)
        self.assertEqual(len(edf.signals_list), edf.n_signals)

    def test_DAT_signal(self):
        # Test that the BinaryCustom class reads data correctly
        text = BinaryCustom("test/data/TAY_FI.DAT")
        self.assertEqual(text.n_signals, 1)
        self.assertEqual(len(text.signals_list), text.n_signals)
        self.assertEqual(type(text.signals_list[0][1]), numpy.float64)


if __name__ == '__main__':
    unittest.main()