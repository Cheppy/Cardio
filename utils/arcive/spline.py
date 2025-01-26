import numpy as np
import matplotlib.pyplot as plt

from cardio.ecg_reader import Signal
import time

class Spline:
    def __init__(self, *args):
        self.h = 1
        self.inside = 0
        self.name  = False
        if len(args) == 1:
            self.__x = [i for i in range(0, len(args[0]))]
            self.__y = args[0]
        elif len(args) == 2:
            self.__x = args[0]
            self.__y = args[1]

        else:
            raise ValueError("You must provide either 1 or 2 arguments.")
        self.__values_x = np.array(self.__x)
        self.__values_y = np.array(self.__y)


        self.F = [(self.__values_y[i - 1] + self.__values_y [i]) / 2 for i in range(1, len(self.__values_y ))]
        self.F_der = [(self.__values_y [i] - self.__values_y [i - 1]) / 1 for i in range(1, len(self.__values_y ))]
        self.x_i = [(self.__values_x[i - 1] + self.__values_x[i]) / 2 for i in range(1, len(self.__values_x))]
        self.d__spline = self.get_spline()

    def __str__(self):
        return str(self.__x)
    def s2_(self, i, x):
        a1 = (self.F_der[i + 1] - self.F_der[i]) / 2 * self.h
        a2 = (self.F_der[i] + self.F_der[i + 1]) * (self.x_i[i] + self.x_i[i + 1]) / 2 * self.h * self.h
        a3 = (self.F[i + 1] - self.F[i]) * (self.x_i[i] + self.x_i[i + 1]) / self.h * self.h * self.h
        a = a1 - a2 + a3
        return (self.F[i + 1] * (x - self.x_i[i]) / (self.x_i[i + 1] - self.x_i[i]) +
                self.F[i] * (x - self.x_i[i + 1]) / (self.x_i[i] - self.x_i[i + 1]) + (x - self.x_i[i]) * (x - self.x_i[i + 1]) * a)


    def get_spline(self):
        x_non, s2 =[], []
        num_subdivisions = 10  # Кількість точок між сусідніми вузлами
        ##xi = xi-1+j
        for i in range(0, len(self.x_i) - 1):
            print("11", len(self.x_i)-1)
            x_sub = np.linspace(self.x_i[i], self.x_i[i + 1], num_subdivisions)
            for x in list(x_sub):
                print("A1", len(x_sub))
                x_non.append(x)
                s2.append(self.s2_(i, x))
        return x_non, s2
             #   s2dx.append(s2_derivative_squared(i, x))

    def new_dots(self):
        x_non1, s21 = self.d__spline
        newRAWX, newRAWY = [], []

        s2n = [0] * 5 + s21 + [0] * 10
        x_non_n = [0] * 5 + x_non1 + [0] * 10

        indices = [i * 10 for i in range(0, len(self.__values_y) + 1)]

        for i in indices:
            if i in range(0, len(s2n) + 1):
                newRAWX.append(i / 10)
                newRAWY.append(s2n[i])
        newRAWY[-1] = self.__values_y[-1]
        newRAWX[-1] = self.__values_x[-1]
        return newRAWX, newRAWY

a =Signal('/test/data/r01.edf')
valuesecg1 = a.signals_list[0]
# valuesecg1 = [0, 2, 6, 5, 8, 1, 9]


class IterativeSpline:
    def __init__(self, values, n=5):
        """
        Initialize the IterativeSpline class.

        :param values: The initial data points to create the first spline.
        :param n: Number of iterations for generating new splines.
        """
        self.values = values
        self.n = n
        self.last_x = None
        self.last_y = None

    def calculate_spline(self):
        """
        Generate the splines iteratively and return the final x and y values.

        :return: The final x and y values of the spline after n iterations.
        """
        # Initial setup for the first spline
        spline = Spline(self.values)
        x, y = spline.d__spline

        self.last_x, self.last_y = x, y  # Store the last spline values

        # Iteratively calculate splines
        for i in range(1, self.n + 1):
            # Get new dots from the previous spline
            new_x, new_y = spline.new_dots()
            print(f"Iteration {i} new dots")

            # Create a new spline with the new dots
            spline = Spline(new_x, new_y)

            # Get the updated spline points
            x, y = spline.d__spline

            # Save the current spline values as the last
            self.last_x, self.last_y = x, y

        # Return the last spline values
        return self.last_x, self.last_y



print(len(valuesecg1))
a = IterativeSpline(valuesecg1,1)
x,y = a.calculate_spline()
end_time = time.time()
plt.plot(valuesecg1[100_000:103_000])
plt.plot(x[100_000:103_000],y[100_000:103_000])
plt.show()
# iterative_spline(valuesecg1, n=105)
