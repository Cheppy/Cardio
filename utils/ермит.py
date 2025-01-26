import numpy as np
import matplotlib.pyplot as plt

from cardio.ecg_reader import Signal
import time


class Spline:
    def __init__(self, *args):
        self.h = 1
        self.inside = 0
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

        self.F = (np.array(self.__values_y[:-1]) + np.array(self.__values_y[1:])) / 2
        self.F_der = (np.array(self.__values_y[1:]) - np.array(self.__values_y[:-1])) / 1
        self.x_i = (np.array(self.__values_x[:-1]) + np.array(self.__values_x[1:])) / 2

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
        num_subdivisions = 10
        num_segments = len(self.x_i) - 1
        x_non = np.empty(num_segments * num_subdivisions)
        s2 = np.empty_like(x_non)

        for i in range(num_segments):
            x_sub = np.linspace(self.x_i[i], self.x_i[i + 1], num_subdivisions)
            s2_values = self.s2_(i, x_sub)
            x_non[i * num_subdivisions:(i + 1) * num_subdivisions] = x_sub
            s2[i * num_subdivisions:(i + 1) * num_subdivisions] = s2_values
        return x_non, s2

    def new_dots(self):
        """
        Generate new points based on the computed spline for further refinement.
        Optimized for performance and clarity.
        """
        _, s21 = self.d__spline

        s2n = np.pad(s21, (5, 10), mode='constant')

        # Generate evenly spaced indices scaled to match the original x-values
        step = 10
        indices = np.arange(0, len(self.__values_y) * step, step)

        # Ensure indices do not exceed the length of the padded array
        indices = indices[indices < len(s2n)]

        # Calculate new x and y values
        newRAWX = indices / step  # Rescale indices to original x-domain
        newRAWY = s2n[indices]

        # Explicitly set the last point to match the original data
        newRAWX[-1] = self.__values_x[-1]
        newRAWY[-1] = self.__values_y[-1]

        return newRAWX, newRAWY


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
        self.spline_calculated = False

    @property
    def coords(self):
        if not self.spline_calculated:
            self.calculate_spline()
        return self.last_x, self.last_y

    def calculate_spline(self):
        """
        Generate the splines iteratively and return the final x and y values.

        :return: The final x and y values of the spline after n iterations.
        """
        print("1", self.values)

        # Initialize the first spline and precompute values
        spline = Spline(self.values)
        self.last_x, self.last_y = spline.d__spline

        # Precompute spline updates only if n > 1
        for _ in range(1, self.n):
            new_dots = spline.new_dots()  # Generate new dots
            spline = Spline(*new_dots)  # Update spline with new dots
            self.last_x, self.last_y = spline.d__spline  # Update final results

        self.spline_calculated = True
        return self.last_x, self.last_y