import math
import numpy as np
from skimage.feature import match_template


def create_ellipse(size, diagonals, sharpness):
    # --- Method information ---
    # create_ellipse creates an image of a diffused ellipse
    #
    # --- Inputs ---
    #   size        : 2x1 list of integers, size of the image to be created
    #   diagonals   : 2x1 list of integers, length of the diagonals of the ellipse
    #   sharpness   : Float, sharpness of the ellipse, value between 0 and 1, where 1 is perfectly sharp
    #
    # --- Outputs ---
    #   mask    : Numpy array, image of the created ellipse

    mask = np.zeros((size[1], size[0]))
    x_moy = diagonals[0] / 2
    y_moy = diagonals[1] / 2
    x_displace = (size[0] - diagonals[0]) / 2
    y_displace = (size[1] - diagonals[1]) / 2
    radius = math.sqrt(x_moy**2 + y_moy**2)
    sharp = (1 - sharpness) ** 2
    for i in range(0, size[1]):
        for j in range(0, size[0]):
            dist = math.sqrt(((j - x_displace + 0.5 - x_moy) / x_moy) ** 2 + ((i - y_displace + 0.5 - y_moy) / y_moy) ** 2)
            if sharpness != 1:
                mask[i][j] = sharp / ((dist - 1) ** 2 + sharp)
            else:
                if (radius*dist <= radius+0.5) & (radius*dist >= radius-1):
                    mask[i][j] = 1
    return mask


def binarize(image, threshold):
    # This method is not used in the program

    dimensions = np.shape(image)
    for i in range(0, dimensions[0]):
        for j in range(0, dimensions[1]):
            if image[i][j] > threshold:
                image[i][j] = 1
            else:
                image[i][j] = 0
    return image


def match_template_full(img, obj):
    # --- Method information ---
    # match_template_full runs the match_template method with an image and a specified object,
    # but also fills in the sides of the returned image such that the size matches that of the original image
    #
    # --- Inputs ---
    #   img : Numpy array, 1D image in which to look for matches
    #   obj : Numpy array, 1D image of the object to use as a reference for finding matches
    #
    # --- Outputs ---
    #   grid: Numpy array, intensity map where high values correspond to a high correlation

    res = match_template(img, obj)
    # Add edges of the image back
    dim_img = np.shape(img)
    dim_obj = np.shape(obj)
    dim_res = np.shape(res)
    grid = np.zeros(dim_img)
    border = (math.floor((dim_obj[0]) / 2), math.floor((dim_obj[1]) / 2))
    for row in range(0, dim_res[0]):
        for col in range(0, dim_res[1]):
            grid[row + border[0]][col + border[1]] = res[row][col]
    return grid



