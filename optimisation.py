import numpy as np
from classes import Point


def average_value(array):
    # --- Method information ---
    # average_value returns the average value of an array
    #
    # --- Inputs ---
    #   array   : Numpy array
    #
    # --- Outputs ---
    #   average : Float, average value of the array

    total = 0
    count = 0
    for row in array:
        for pixel in row:
            if pixel != 0:
                total += pixel
                count += 1
    if count != 0:
        average = total / count
    else:
        average = 0
    return average


def find_local_maxima(image, order, threshold):
    # --- Method information ---
    # find_local_maxima is a very basic optimisation method to find local maxima. For every pixel in the image,
    # it checks whether this pixel has the highest value of the surrounding pixels, specified by the order variable
    #
    # --- Inputs ---
    #   image       : Numpy array
    #   order       : Integer, number of pixels to be checked in each direction
    #   threshold   : Float, minimal acceptable value for a pixel to be considered a maximum
    #
    # --- Outputs ---
    #   list_of_maxima  : List of point objects

    list_of_maxima = []
    dim = np.shape(image)
    for row in range(order, dim[0]+1-order):
        for col in range(order, dim[1]+1-order):
            if image[row, col] >= threshold:
                maximum = np.amax(image[row - order:row + order + 1, col - order:col + order + 1])
                if image[row, col] >= maximum:
                    list_of_maxima.append(Point(row, col))
    return list_of_maxima



