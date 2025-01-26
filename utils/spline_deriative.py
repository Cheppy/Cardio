import time

import matplotlib.pyplot as plt

from cardio.ecg_reader import Signal

from utils.ермит import IterativeSpline

a =Signal('/Users/mykolayefremov/Documents/projects/Cardio/test/data/r01.edf')
valuesecg1 = a.signals_list[0]
valuesecg1 = [0, 2, 6, 5, 8, 1, 9]

splined =  IterativeSpline(valuesecg1, 1)
plt.plot(valuesecg1)
start1 = time.time()
x,y = splined.coords
endq = time.time()

print(x)
print(y)
plt.plot(x,y)
plt.show()
print("splined calculation: ", endq-start1      )

