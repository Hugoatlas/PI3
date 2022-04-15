import math
from classes import Point


class Particle:
    def __init__(self, contour):
        # Ordered list of point objects which constitute the contour of the particle
        # No points should be repeated in the contour
        self.contour = contour
        # Point object corresponding to the center in space
        self.center = get_center(contour)
        # Area of the polygonal approximation of the particle
        self.area = get_area(contour)
        # Perimeter of the polygonal approximation of the particle
        self.perimeter = get_perimeter(contour)
        # Radius of the polygonal approximation of the particle, based on a ratio of the area and perimeter
        self.radius = get_radius(contour)
        # Circularity of the polygonal approximation of the particle
        self.circularity = get_circularity(contour)
        # Another measure of the radius, based on the average value of the distance between
        # each contour point and the center
        self.radial_average = get_radial_average(contour)
        # Standard deviation that accompanies the above radial average
        self.radial_sd = get_radial_standard_deviation(contour)
        # Standard deviation on the radial distance difference between two consecutive contour points.
        # When this value is high, this can indicate that the contour is very 'rough'
        self.radial_sd_consecutive = get_radial_difference_sd(contour)


def get_line_length(a, b):
    # The method takes in two point objects and returns the pythagorean distance between them
    length = math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)
    return length


def get_triangle_area(a, b, c):
    # This method takes in three point objects and returns the area of the triangle described
    area = abs(a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2
    return area


def get_center(contour):
    # --- Method information ---
    # get_center finds the center of a polygonal contour, based on the 'center of mass' of all the contour segments
    #
    # --- Inputs ---
    #   contour : Ordered list of point objects corresponding to the closed contour of a polygon
    #
    # --- Outputs ---
    #   center  : Point object

    # There are some precautions to avoid errors and divisions by zero.
    if len(contour) > 0:
        moment_0 = Point(0, 0)
        p = get_perimeter(contour)
        prev_point = contour[len(contour)-1]
        for point in contour:
            moment_0.x += get_line_length(prev_point, point) * (point.x + prev_point.x) / 2
            moment_0.y += get_line_length(prev_point, point) * (point.y + prev_point.y) / 2
            prev_point = point
        if p != 0:
            center = Point(moment_0.x / p, moment_0.y / p)
        else:
            center = Point(0, 0)
    else:
        center = Point(0, 0)

    return center


def get_perimeter(contour):
    # --- Method information ---
    # get_perimeter calculates the sum of the distances between consecutive points in the contour, thus returns
    # the perimeter of the contour
    #
    # --- Inputs ---
    #   contour : Ordered list of point objects corresponding to the closed contour of a polygon
    #
    # --- Outputs ---
    #   perimeter   : Float, perimeter of the contour

    # There are some precautions to avoid errors and divisions by zero.
    if len(contour) > 0:
        perimeter = 0
        prev_point = contour[len(contour) - 1]
        for point in contour:
            perimeter += get_line_length(point, prev_point)
            prev_point = point
    else:
        perimeter = 0

    return perimeter


def get_area(contour):
    # --- Method information ---
    # get_area calculates the sum of the areas of the triangles formed by two consecutive contour points and the center
    # of the contour, thus returns the area described by the contour.
    # NOTE : For this method to be accurate, no overlap is permitted on the triangles. Because of the way the contour
    # is constructed, this condition is always met for this program.
    #
    # --- Inputs ---
    #   contour : Ordered list of point objects corresponding to the closed contour of a polygon
    #
    # --- Outputs ---
    #   area    : Float, area of the contour

    # There are some precautions to avoid errors and divisions by zero.
    if len(contour) > 0:
        area = 0
        center = get_center(contour)
        prev_point = contour[len(contour) - 1]
        for point in contour:
            area += get_triangle_area(point, prev_point, center)
            prev_point = point
    else:
        area = 0

    return area


def get_radius(contour):
    # --- Method information ---
    # get_radius calculates a ratio between the area and the perimeter to approximate the radius of the circle
    # described. The radius is also corrected for a circular approximation based on the number of points in the
    # contour. This is mostly noticeable when the number of points is very low.
    #
    # --- Inputs ---
    #   contour : Ordered list of point objects corresponding to the closed contour of a polygon
    #
    # --- Outputs ---
    #   r   : Float, radius of the contour

    # There are some precautions to avoid errors and divisions by zero.
    if len(contour) > 0:
        perimeter = get_perimeter(contour)
        area = get_area(contour)
        if perimeter != 0:
            r = 2 * area / perimeter
            # Circular adjustment on the value of r for the number of points in the polygonal approximation
            # (Comment line below to disable)
            r = r / math.cos(math.pi / len(contour))
        else:
            r = 0
    else:
        r = 0

    return r


def get_radial_average(contour):
    # --- Method information ---
    # get_radial_average calculates the average distance between each contour point and the contour center,
    # thus returns a second approximation for the radius of the particle.
    #
    # --- Inputs ---
    #   contour : Ordered list of point objects corresponding to the closed contour of a polygon
    #
    # --- Outputs ---
    #   r   : Float, radius of the contour

    # There are some precautions to avoid errors and divisions by zero.
    if len(contour) > 0:
        center = get_center(contour)
        moment_0 = 0
        moment_1 = 0
        for point in contour:
            radius = get_line_length(point, center)
            moment_0 += 1
            moment_1 += radius
        if moment_0 != 0:
            r = moment_1 / moment_0
        else:
            r = 0
    else:
        r = 0

    return r


def get_radial_variance(contour):
    # --- Method information ---
    # get_radial_variance calculates the variance on the distances between each contour point and the contour center
    #
    # --- Inputs ---
    #   contour : Ordered list of point objects corresponding to the closed contour of a polygon
    #
    # --- Outputs ---
    #   variance: Float, variance on the second evaluation of the radius

    # There are some precautions to avoid errors and divisions by zero.
    if len(contour) > 0:
        center = get_center(contour)
        average_radius = get_radial_average(contour)
        moment_0 = 0
        moment_1 = 0
        for point in contour:
            radius = get_line_length(point, center)
            moment_0 += 1
            moment_1 += (radius - average_radius) ** 2
        if moment_0 != 0:
            variance = moment_1 / moment_0
        else:
            variance = 0

    else:
        variance = 0

    return variance


def get_radial_standard_deviation(contour):
    # This method returns the standard deviation on the radius of the contour
    sd = math.sqrt(get_radial_variance(contour))
    return sd


def get_radial_difference_variance(contour):
    # --- Method information ---
    # get_radial_difference_variance calculates the variance on the radial distance differences
    # between each consecutive contour point
    #
    # --- Inputs ---
    #   contour : Ordered list of point objects corresponding to the closed contour of a polygon
    #
    # --- Outputs ---
    #   variance: Float

    # There are some precautions to avoid errors and divisions by zero.
    if len(contour) > 0:
        center = get_center(contour)
        prev_radius = get_line_length(contour[len(contour) - 1], center)
        moment_0 = 0
        moment_1 = 0
        for point in contour:
            radius = get_line_length(point, center)
            moment_0 += 1
            moment_1 += (radius - prev_radius) ** 2
            prev_radius = radius
        if moment_0 != 0:
            variance = moment_1 / moment_0
        else:
            variance = 0

    else:
        variance = 0

    return variance


def get_radial_difference_sd(contour):
    # This method returns the standard deviation on the difference of consecutive radial distances
    sd = math.sqrt(get_radial_difference_variance(contour))
    return sd


def get_outliers(contour, r, sd, thresh):
    # --- Method information ---
    # get_outliers finds outlier points in the contour and returns a list containing the index of such points.
    # These points are found using simple statistical analysis on the distance between a contour point and the center
    # of the contour (z1), and on the difference of the radial distance between two consecutive contour points (z2).
    # It is assumed that these two random variables are normally distributed.
    #
    # --- Inputs ---
    #   contour : Ordered list of point objects corresponding to the closed contour of a polygon
    #   r       : Float, average radius of the particle
    #   sd      : Float, standard deviation on the radius of the particle, or of a set of similar particles
    #   thresh  : Float, threshold value to use for the hypothesis test
    #
    # --- Outputs ---
    #   outliers: List of the indexes of outlier points

    # There are some precautions to avoid errors and divisions by zero.
    outliers = []
    i = 0
    if sd != 0:
        center = get_center(contour)
        prev_radius = get_line_length(contour[len(contour) - 1], center)
        diff_sd = math.sqrt(get_radial_difference_variance(contour))
        for point in contour:
            radius = get_line_length(point, center)
            z1 = (radius - r) / sd
            z2 = (radius - prev_radius) / diff_sd
            if abs(z1) > thresh:
                outliers.append(i)
            elif abs(z2) > thresh:
                r1 = radius - r
                r2 = prev_radius - r
                if abs(r1) > abs(r2):
                    outliers.append(i)
                else:
                    if i != 0:
                        outliers.append(i - 1)
                    else:
                        outliers.append(len(contour) - 1)
            i += 1
            prev_radius = radius

    # Remove duplicates and reorder list
    outliers = sorted(list(dict.fromkeys(outliers)))

    return outliers


def get_circularity(contour):
    # --- Method information ---
    # get_circularity calculates a ratio between the area and the perimeter to evaluate the circularity of the
    # contour
    #
    # --- Inputs ---
    #   contour : Ordered list of point objects corresponding to the closed contour of a polygon
    #
    # --- Outputs ---
    #   c   : Float, circularity of the particle

    # There are some precautions to avoid errors and divisions by zero.
    if len(contour) > 0:
        perimeter = get_perimeter(contour)
        area = get_area(contour)
        if perimeter != 0:
            c = 4 * math.pi * area / (perimeter ** 2)
        else:
            c = 0
    else:
        c = 0

    return c


def append_particle(particle_list, new_particle, para):
    # --- Method information ---
    # append_particle tries to update the list of particles based on a new particle to be added.
    # If the new particle is good enough to be added, it checks whether it should replace other particles from the list
    # and does so if necessary
    #
    # --- Inputs ---
    #   particles_list  : List of particle objects to be filled
    #   new_particle    : Particle object to be added to the list
    #   para            : Search object, containing the search settings
    #
    # --- Outputs ---
    #   particle_list   : List of particle objects, updated
    #   add_particle    : Boolean variable to specify whether the particle was added or not

    dist_tol = para.contour_para.dist_tol
    circ_tol = para.contour_para.circ_tol
    nb_tol, nb_points = para.contour_para.nb_tol, para.contour_para.nb_points

    flags = []              # Keep track of flagged particles, to remove from list
    add_particle = True     # Append new_particle to list if this variable remains True
    count = 0

    if new_particle.circularity < circ_tol:
        add_particle = False
    elif len(new_particle.contour) < nb_tol * nb_points:
        add_particle = False

    # Check the new particle does not interfere with any other particles
    # If so, remove interfering particles or specify not to add new particle to list
    if len(particle_list) > 0 and add_particle:
        for particle in particle_list:
            dist = math.sqrt((particle.center.x-new_particle.center.x)**2 + (particle.center.y-new_particle.center.y)**2)
            if dist < dist_tol*(particle.radius + new_particle.radius):
                if new_particle.circularity >= particle.circularity:
                    flags.append(count)
                else:
                    add_particle = False
                    break

            count += 1

    # If new particle is valid, remove flagged particles from list and/or append the new particle
    if add_particle:
        for flag in reversed(flags):
            particle_list.pop(flag)
        particle_list.append(new_particle)

    return particle_list, add_particle
