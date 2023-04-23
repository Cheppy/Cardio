import unittest
import numpy as np
import os
from cardio import ecg_reader


class TestEDFReader(unittest.TestCase):

    def setUp(self):
        self.edf_file_path = './test/data/r01.edf'
        self.edf_entity = ecg_reader.EDF(self.edf_file_path)

    def tearDown(self):
        pass

    def test_read_edf(self):
        # Positive tests
        self.assertEqual(self.edf_entity.n_signals, 5)
        self.assertListEqual(self.edf_entity.labels, ['Direct_1', 'Abdomen_1',
                                                      'Abdomen_2', 'Abdomen_3', 'Abdomen_4'])

        self.assertIsInstance(self.edf_entity.signals_list, list)
        self.assertTrue(lambda: all((isinstance(item, np.ndarray) or list) for item in self.edf_entity.signals_list))
        self.assertEqual(len(self.edf_entity.signals_list), 5)

        self.assertIsInstance(self.edf_entity.signals_list[0], np.ndarray or list)

        # Negative tests
        with self.assertRaises(FileNotFoundError):
            ecg_reader.EDF('imaginary_file.edf')


    def test_get_signal_by_index(self):
        # Positive tests
        self.edf_entity.get_signal_by_index(2)
        signal_0 = self.edf_entity.get_signal_by_index(0)
        signal_1 = self.edf_entity.get_signal_by_index(1)
        self.assertIsInstance(signal_0, np.ndarray)
        self.assertIsInstance(signal_1, np.ndarray)

        # Edge cases
        signal_0_part = self.edf_entity.get_signal_by_index(0, start=100, end=200)
        self.assertIsInstance(signal_0_part, np.ndarray)
        self.assertEqual(signal_0_part.shape[0], 100)
        signal_0_part = self.edf_entity.get_signal_by_index(0, start=-100)
        self.assertIsInstance(signal_0_part, np.ndarray)

        signal_1_part = self.edf_entity.get_signal_by_index(1, end=-100)
        self.assertIsInstance(signal_1_part, np.ndarray)

        with self.assertRaises(ValueError):
            self.edf_entity.get_signal_by_index(len(self.edf_entity.signals_list)+3)
