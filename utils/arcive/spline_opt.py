import numpy as np
import matplotlib.pyplot as plt

from cardio.ecg_reader import Signal
import time


class Spline:
    def __init__(self, *args):
        print(args)
        self.h = 391
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


        self.F = [(self.__values_y[i - 1] + self.__values_y [i]) / 2 for i in range(1, len(self.__values_y ))]
        self.F_der = [(self.__values_y [i] - self.__values_y [i - 1]) / 1 for i in range(1, len(self.__values_y ))]
        self.x_i = [(self.__values_x[i - 1] + self.__values_x[i]) / 2 for i in range(1, len(self.__values_x))]
        self.d__spline = self.get_spline()

    def __str__(self):
        return str(self.__x)

    def s2_(self, i, x):

        # Convert scalar operations to array operations
        a1 = (self.F_der[i + 1] - self.F_der[i]) / (2 * self.h)
        a2 = (self.F_der[i] + self.F_der[i + 1]) * (self.x_i[i] + self.x_i[i + 1]) / (2 * self.h ** 2)
        a3 = (self.F[i + 1] - self.F[i]) * (self.x_i[i] + self.x_i[i + 1]) / (self.h ** 3)
        a = a1 - a2 + a3

        # Vectorized computation of s2 values
        x_diff = x - self.x_i[i]
        x_diff_next = x - self.x_i[i + 1]
        s2_values = (
                self.F[i + 1] * x_diff / (self.x_i[i + 1] - self.x_i[i])
                + self.F[i] * x_diff_next / (self.x_i[i] - self.x_i[i + 1])
                + x_diff * x_diff_next * a
        )
        return s2_values

    def get_spline(self):
        num_subdivisions = 10
        x_non = []
        s2 = []

        # Precompute array sizes
        num_segments = len(self.x_i) - 1
        print(num_segments)
        print(num_subdivisions)
        x_non = np.empty(num_segments * num_subdivisions)
        s2 = np.empty_like(x_non)

        start_time = time.time()

        for i in range(num_segments):
            # Vectorize linspace generation
            x_sub = np.linspace(self.x_i[i], self.x_i[i + 1], num_subdivisions)

            # Compute s2 values directly for the entire range
            s2_values = self.s2_(i, x_sub)

            # Assign to the preallocated arrays
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
start_time = time.time()
# a =Signal('/Users/mykolayefremov/Documents/projects/Cardio/test/data/r01.edf')
# valuesecg1 = a.signals_list[0]
end_time = time.time()
print(f"Execution time for `calculate_spline`: {end_time - start_time:.6f} seconds")

valuesecg1 = [0, 2, 6, 5, 8, 1, 9]


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
        print("1", self.values)
        spline = Spline(self.values)
        x, y = spline.d__spline

        self.last_x, self.last_y = x, y  # Store the last spline values
        if self.n >=2:
            for i in range(1, self.n-1):
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


def find_local_maxima(porig, threshold):
    # Initialize an empty list to store the local maxima
    local_maxima = []

    # Iterate through the list, checking each element except the first and last one
    for i in range(1, len(porig) - 1):
        # Check if the value is greater than or equal to the threshold and it's a local maximum
        if porig[i] >= threshold and porig[i] > porig[i - 1] and porig[i] > porig[i + 1]:
            local_maxima.append(porig[i])

    # Also check the first and last elements for local maxima (they can only have one neighbor)
    if len(porig) > 0 and porig[0] >= threshold and porig[0] > porig[1]:
        local_maxima.append(porig[0])
    if len(porig) > 1 and porig[-1] >= threshold and porig[-1] > porig[-2]:
        local_maxima.append(porig[-1])

    return local_maxima


start_time = time.time()
plt.plot(valuesecg1)




a = IterativeSpline(valuesecg1,1)
x,y = a.calculate_spline()
plt.plot(x,y, 'o')
plt.show()
print(len(y))

# iterative_spline(valuesecg1, n=105)
