import math
import numpy as np

from classes import Point
from matchObject import create_ellipse


class Pixel:
    def __init__(self, value, pixel):
        self.value = value
        self.pixel = pixel


def take_first_element(elem):
    # take_first_element returns the first element from the list
    return elem[0]


def find_radial_edge(grid, start_point, dir_vector, tol):
    # --- Method information ---
    # find_radial_edge finds the highest value of on the radial axis defined by a direction vector and a starting point
    #
    # --- Inputs ---
    #   grid        : Numpy array containing the values to be checked
    #   start_point : Point object defining the starting point of the line on the grid
    #   dir_vector  : Point object defining the direction (or slope) of the line
    #   tol         : Float, minimum value at which a point is considered acceptable
    #
    # --- Outputs ---
    #   best_fits   : List of pixel objects found on the line, ordered from highest to lowest value

    grid_size = np.shape(grid)
    vector_list = []
    best_fits = []
    dt = 0.5

    pix_x = 0
    pix_y = 0
    done = False
    safety_count = 0
    for direction in (1, -1):
        t = 0
        while (not done) and (safety_count < 1000):
            x = start_point.x + t * direction * dir_vector.x
            y = start_point.y + t * direction * dir_vector.y

            if (pix_x != round(x)) or (pix_y != round(y)):
                pix_x = round(x)
                pix_y = round(y)

                if (0 <= pix_x < grid_size[0]) and (0 <= pix_y < grid_size[1]):
                    pixel_value = grid[pix_x, pix_y]
                    if pixel_value > tol:
                        vector_list.append(Pixel(pixel_value, Point(pix_x, pix_y)))
                else:
                    done = True

            safety_count += 1
            t += dt

    if len(vector_list) > 0:
        # sorted_list = sorted(vector_list, key=take_first_element, reverse=True)
        sorted_list = sorted(vector_list, key=lambda z: getattr(z, 'value'), reverse=True)
        for element in sorted_list:
            best_fits.append(element.pixel)

    return best_fits


def translate_points(points, trans):
    # --- Method information ---
    # translate_points is used to translate point objects by a vector
    #
    # --- Inputs ---
    #   points  : List of point objects to be translated
    #   trans   : Point object containing the translation vector
    #
    # --- Outputs ---
    #   new_points  : List of point objects, translated points

    new_points = []
    for point in points:
        new_points.append(Point(point.x + trans.x, point.y + trans.y))
    return new_points


def scale_points(points, scale, do_round):
    # --- Method information ---
    # scale_points is used to scale point objects by a certain factor
    #
    # --- Inputs ---
    #   points  : List of point objects to be scaled by a factor
    #   scale   : Point object, factor by which to scale the points x and y component
    #   do_round: Boolean variable to specify if the resulting points' coordinates should be rounded or not
    #
    # --- Outputs ---
    #   new_points  : List of point objects, scaled points

    new_points = []
    for point in points:
        if do_round:
            new_points.append(Point(round(point.x * scale.x), round(point.y * scale.y)))
        else:
            new_points.append(Point(point.x * scale.x, point.y * scale.y))
    return new_points


def detect_circle_edge_points(grid, center, r, para):
    # --- Method information ---
    # detect_circle_edge_points takes in a contour map of an image expected to contain a circle, as well as
    # information concerning this circle. It returns an ordered list of points constructing the closed edge of the
    # circle.
    #
    # --- Inputs ---
    #   grid    : 2D binary numpy array containing the image edges (255 is an edge, 0 is not an edge)
    #   center  : Pixel in the image corresponding to middle of the expected circle
    #   r       : Expected radius of the circle
    #   para    : Search parameters object
    #
    # --- Outputs ---
    #   list_of_points : Ordered list of points constructing the actual edge of the expected circle
    #   list_of_directions : A complicated thing to explain, which is not used by the program

    n = para.contour_para.nb_points
    sharpness = para.contour_para.sharpness
    radial_tol = para.contour_para.radial_tol

    # Get dimensions for creation of circular mask.
    size = np.shape(grid)
    r = round(r)
    x_size = round(max(size[0] - center.x, center.x))
    y_size = round(max(size[1] - center.y, center.y))
    mask = create_ellipse((2*x_size, 2*y_size), (2*r, 2*r), sharpness)

    # Apply circular mask on edge map.
    # Deal with potential "spilling" over the edge from the mask.
    # create a new grid to store information.
    grid_weight = grid
    displacement = [0, 0]
    if center.x < (size[0] / 2):
        displacement[0] = int(max(size[0] - 2*center.x, 0))
    if center.y < (size[1] / 2):
        displacement[1] = int(max(size[1] - 2*center.y, 0))

    for i in range(0, size[0]):
        for j in range(0, size[1]):
            grid_weight[i, j] = grid[i, j] * mask[(i + displacement[0]), (j + displacement[1])]

    # Create a list of evenly distributed points on the expected edge of the circle.
    # For every expected edge point, try to find the best actual edge point in the edge map.
    list_of_points = []
    list_of_directions = []
    for i in range(0, n):
        theta = 2 * math.pi * i / n
        dir_vector = Point(math.cos(theta), math.sin(theta))

        # Find the highest valued pixels on the corresponding radial direction.
        # These correspond to the most likely edge pixels.
        best_fits = find_radial_edge(grid, center, dir_vector, radial_tol)
        list_of_directions.append(best_fits)

        # Check best_fit is not empty.
        if len(best_fits) > 0:
            list_of_points.append(best_fits[0])

    return list_of_points, list_of_directions


