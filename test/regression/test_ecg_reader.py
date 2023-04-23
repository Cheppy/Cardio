import datetime

import numpy as np

from cardio import ecg_reader as ecgread


def test_ecg_reader_read():
    """reading edf file """
    edf_reader = ecgread.EDF(edf_path="test/data/r01.edf")
    valid_r01_header = {'technician': '', 'recording_additional': '',
                    'patientname': 'X', 'patient_additional': '',
                    'patientcode': 'r01', 'equipment': 'Komporel',
                    'admincode': '', 'gender': 'Female',
                    'startdate': datetime.datetime(2011, 1, 1, 0, 0),
                    'birthdate': ''}

    assert edf_reader.header == valid_r01_header
    assert edf_reader.n_signals == 5

    assert edf_reader.labels == ['Direct_1', 'Abdomen_1', 'Abdomen_2', 'Abdomen_3', 'Abdomen_4']
    assert len(edf_reader.signals_list[0]) > 0
    assert len(edf_reader.signals_list[1]) > 0


def test_get_signal_by_index():
    edf_reader = ecgread.EDF(edf_path="test/data/test_eeg.edf")
    edf_reader.read_edf()
    signal_1 = edf_reader.get_signal_by_index(0)
    assert len(signal_1) > 0
    assert signal_1[0] == edf_reader.signals_list[0][0]
    assert signal_1[-1] == edf_reader.signals_list[0][-1]
    signal_2 = edf_reader.get_signal_by_index(1, start=100, end=200)
    assert len(signal_2) == 100
    assert signal_2[0] == edf_reader.signals_list[1][100]
    assert signal_2[-1] == edf_reader.signals_list[1][199]





