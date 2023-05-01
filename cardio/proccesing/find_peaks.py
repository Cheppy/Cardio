import random
import numpy as np
from scipy.signal import find_peaks
from matplotlib import pyplot as plt
from cardio import ecg_reader

HEIGHT_R = 220
MAX_OCRP, MAX_OCRM = 250,250

HEIGHT_EXTR = 100
MAX_EXTRAOCRP, MAX_EXTRAOCRM = 20, 20

#FROM CONTENT ROOT
TAYDATA = ecg_reader.Signal('test/data/FI_SGL.DAT')
TAY_SIGNAL = TAYDATA.signals_list[0]

y_list = TAY_SIGNAL#[2003:5400]

h = np.diff(y_list)**2
data = np.array(h)

max_indices, _ = find_peaks(data, height=HEIGHT_R)

fig1, ax1 = plt.subplots()

max_indices_okresnost = []
max_yks_in_graph = []

for x in max_indices:
    max_indices_okresnost.append((x-250,x+250))

for x in max_indices_okresnost:
    yks = []
    maxi = x[1]
    if x[1] > len(y_list):
        maxi = len(y_list)-1
    for xsi in range(x[0], maxi):
        yks.append(y_list[xsi])
    max_yks_in_graph.append(max(yks))

maximums_x, maximums_y = [], []

for xb, yb in enumerate(y_list):
    if yb in max_yks_in_graph and xb != 0 and xb != len(y_list)-1:
        maximums_x.append(xb)
        maximums_y.append(yb)

plt.plot(y_list)
plt.scatter(maximums_x, maximums_y, color='red')
plt.show()


r_peaks = maximums_y
ecg_data = y_list

p_pairs = []
for p_peak in r_peaks:
    left_idx = None
    right_idx = None
    p_peak_index = np.where(ecg_data == p_peak)[0][0]
    for i in range(p_peak_index, 0, -1):
        if ecg_data[i] < 0:
            left_idx = i
            break
    for i in range(p_peak_index, len(ecg_data)):
        if ecg_data[i] < 0:
            right_idx = i
            break
    p_pairs.append((left_idx, right_idx))

sublists_y = [ecg_data[p_pairs[i][1]+1:p_pairs[i+1][0]+1] for i in range(len(p_pairs)-1)]
sublists_x = [list(range(p_pairs[i][1]+1, p_pairs[i+1][0]+1)) for i in range(len(p_pairs)-1)]

colors = ['#{:06x}'.format(random.randint(0, 256**3-1)) for i in range(len(sublists_y))]

# строим график для каждого подсписка
plt.figure(figsize=(10,5))
for i, sublist in enumerate(sublists_y):
    plt.plot(sublists_x[i], sublist, color=colors[i%len(colors)])
plt.show()

# Find extrasystoles in a selected sublist
INDEX_EXTRA = 4
x, y = sublists_x[INDEX_EXTRA], sublists_y[INDEX_EXTRA]

y_diff = np.diff(y)**2

# Find local maxima in y_diff as potential R-peaks
x_local, _ = find_peaks(y_diff, height=HEIGHT_EXTR)

#DEBUG
to_tst = []
for idx in x_local:
    to_tst.append(y_diff[idx])
    print(f"Local maximum: {y_diff[idx]}, Index: {idx}")

okrestnost2 = [(x-MAX_EXTRAOCRM, x+MAX_EXTRAOCRP) for x in x_local]

max_yks2 = []
for x in okrestnost2:
    ykso = []
    maxi = x[1]
    if x[1] > len(y):
        maxi = len(y)-1
    for xsi in range(x[0], maxi):
        ykso.append(y[xsi])
    max_yks2.append(max(ykso))

#EXTRASISTOLS:
extray = []
extrax = []
for xbi, ybi in enumerate(y):
    if ybi in max_yks2:
        idx = np.where(y_list == ybi)[0]
        if len(idx) > 0 and ybi not in maximums_y:
            extrax.append(idx[0])
            extray.append(ybi)

fg, ax = plt.subplots()
plt.plot(sublists_x[INDEX_EXTRA], sublists_y[INDEX_EXTRA])
ax.scatter(extrax, extray, color='orange')
plt.show()
