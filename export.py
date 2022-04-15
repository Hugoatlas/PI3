import pickle
import cv2


def save_data(data, filename):
    # --- Method information ---
    # save_data saves data into a .dat file
    #
    # --- Inputs ---
    #   data    : Any sort of data, such as a list containing objects for example
    #   filename: Source of the file in which data is to be saved
    #
    # --- Outputs ---
    #   This method does not have a return statement

    output_file = open(filename, 'wb')
    pickle.dump(data, output_file)


def open_data(filename):
    # --- Method information ---
    # open_data retrieves data from a previously saved .dat file
    #
    # --- Inputs ---
    #   filename: Source of the file in which data is to be saved
    #
    # --- Outputs ---
    #   data    : Any sort of data, such as a list containing objects for example

    input_file = open(filename, 'rb')
    data = pickle.load(input_file)
    return data


def convert_particles_data(particles_list):
    # --- Method information ---
    # convert_particles_data is used to convert the particles_list list into a list of particles
    #
    # --- Inputs ---
    #   particles_list  : List of the list of particles, sorted by image
    #
    # --- Outputs ---
    #   data    : List of all particles

    data = []
    for particles in particles_list:
        for particle in particles:
            data.append(particle)
    return data


def save_particles_to_images(images_list, particles_list, images_src):
    # --- Method information ---
    # save_particles_to_images is used to print particles contours on the corresponding image,
    # and save the resulting image
    #
    # --- Inputs ---
    #   images_list     : List of images, of same length and order as particles_list
    #   particles_list  : List of the list of particles, sorted by image
    #   images_src      : Source of the folder in which the resulting images are to be saved
    #
    # --- Outputs ---
    #   This method does not have a return statement

    for i in range(0, len(particles_list)):
        image = print_particles(images_list[i], particles_list[i])
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(f'{images_src}/image_{i}.jpg', image)


def draw_segment(image, point_a, point_b, color, thickness):
    # --- Method information ---
    # draw_segment is used to draw a line segment between two points in an image
    #
    # --- Inputs ---
    #   image       : Numpy array, it is the image in which the segment is to be drawn
    #   point_a     : Point object, starting point of the segment
    #   point_b     : Point object, end point of the segment
    #   color       : Tuple, color of the line segment in BGR
    #   thickness   : Integer value, thickness of the line segment in pixels
    #
    # --- Outputs ---
    #   result      : Numpy array, image with the segment drawn on it

    result = image.copy()
    result = cv2.line(result, (point_a.y, point_a.x), (point_b.y, point_b.x), color, thickness)
    return result


def draw_particle_contour(image, particle, color, thickness):
    # --- Method information ---
    # draw_particle_contour is used to draw the contour of one particle on an image
    #
    # --- Inputs ---
    #   image       : Numpy array, it is the image in which contour is to be drawn
    #   particle    : Particle object
    #   color       : Tuple, color of the line segment in BGR
    #   thickness   : Integer value, thickness of the line segment in pixels
    #
    # --- Outputs ---
    #   result      : Numpy array, image with the contour drawn on it

    contour = particle.contour
    result = image.copy()
    n = len(contour)
    if n > 0:
        prev_point = contour[n - 1]
        for i in range(0, n):
            result = draw_segment(result, contour[i], prev_point, color, thickness)
            prev_point = contour[i]

    return result


def print_particles(image, particles_list):
    # --- Method information ---
    # print_particles is used to draw the contours of all particles form a list on an image
    #
    # --- Inputs ---
    #   image           : Numpy array, it is the image in which the segment is to be drawn
    #   particles_list  : List of particle objects
    #
    # --- Outputs ---
    #   result      : Numpy array, image all contours drawn on it

    results = image.copy()
    for obj in particles_list:
        results = draw_particle_contour(results, obj, color=(255, 0, 0), thickness=2)
    return results
