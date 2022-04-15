import numpy as np
import cv2

from classes import Point
from constructContour import detect_circle_edge_points, translate_points, scale_points
from matchObject import create_ellipse, match_template_full
from analyseContour import Particle, append_particle, get_radial_average, get_radial_standard_deviation, get_outliers
from optimisation import find_local_maxima
from skimage.feature import match_template


def resize_image(image, scale_factor):
    # --- Method information ---
    # resize_image resizes an image by a certain factor
    #
    # --- Inputs ---
    #   image       : Numpy array, the image to be resized
    #   scale_factor: Float, factor by which to resize the image
    #
    # --- Outputs ---
    #   img : Numpy array, resized image

    image_size = np.shape(image)
    new_size = (round(scale_factor * image_size[1]), round(scale_factor * image_size[0]))
    img = cv2.resize(image, new_size)
    return img


def rescale_image(image, max_dim):
    # --- Method information ---
    # rescale_image resizes an image such that none of its dimensions are greater than a specified limit
    #
    # --- Inputs ---
    #   image   : Numpy array, the image to be resized
    #   max_dim : Integer, maximum dimension allowable
    #
    # --- Outputs ---
    #   img         : Numpy array, resized image
    #   scale_factor: Float, factor by which to resize the image

    # Get size of actual image. Make sure the largest dimension is less than a specified value.
    # If not, calculate scale factor and apply it on both dimensions of the image.
    image_size = np.shape(image)
    max_image_dim = max(image_size)
    scale_factor = 1
    if max_image_dim > max_dim:
        scale_factor = max_dim / max_image_dim
    img = resize_image(image, scale_factor)

    return img, scale_factor


def normalize_image(image):
    # --- Method information ---
    # normalize_image normalizes the values contained in an image, such that the lowest is 0 and the highest is 1
    #
    # --- Inputs ---
    #   image   : Numpy array, the image to be normalized
    #
    # --- Outputs ---
    #   normalized_image    : Numpy array, normalized image

    max_value = np.amax(image)
    min_value = np.amin(image)
    normalized_image = image.copy()
    if max_value != min_value:
        normalized_image = (normalized_image - min_value) / (max_value - min_value)
    return normalized_image


def adjust_colors(image, weights):
    # --- Method information ---
    # adjust_colors scales the color components of an image by specified weights
    #
    # --- Inputs ---
    #   image   : Numpy array, the image to be adjusted
    #   weights : 3x1 list of floats
    #
    # --- Outputs ---
    #   result  : Numpy array, image with adjusted colors

    result = image.copy()
    for i in range(0, len(weights)):
        result[:, :, i] = result[:, :, i] * weights[i]
    return result


def compose_colors(image, composition):
    # --- Method information ---
    # compose_colors returns a 1D image where each pixel is a linear composition of the colors of this pixel
    #
    # --- Inputs ---
    #   image       : Numpy array, the image to be processed where each pixel has as many values as the composition list
    #   composition : 3x1 list of floats
    #
    # --- Outputs ---
    #   result  : Numpy array, processed image with each pixel being assigned only one value

    img_copy = image.copy()
    dim = np.shape(img_copy)
    result = np.zeros((dim[0], dim[1]))
    for i in range(0, len(composition)):
        result[:, :] += img_copy[:, :, i] * composition[i]

    result = 255 * normalize_image(result)
    # For now, creation of an image to provide a path for Canny method
    cv2.imwrite('write.jpg', result)
    result = cv2.imread('write.jpg', 0)
    return result


def get_dominant_color(image):
    # This method is not used in the program

    # This method will return an image where each pixel will be only of its dominant color
    img_dim = image.shape
    result = np.zeros((img_dim[0], img_dim[1]))
    rgb = [0, 0, 0]
    for i in range(0, img_dim[0]):
        for j in range(0, img_dim[1]):
            maximum = 0
            for k in range(0, img_dim[2]):
                if image[i, j, k] > maximum:
                    maximum = image[i, j, k]
                    result[i, j] = k

            for n in range(0, img_dim[2]):
                if result[i, j] == n:
                    rgb[n] += 1

    return result, rgb


def get_color_differences(image, weights):
    # --- Method information ---
    # get_color_differences returns a 1D image where the values are a weighted sum of the color differences
    #
    # --- Inputs ---
    #   image   : Numpy array, RGB image to be processed
    #   weights : 3x1 list of floats
    #
    # --- Outputs ---
    #   result  : Numpy array, processed image with each pixel being assigned only one value

    diff_rg = compose_colors(image, (1, -1, 0))
    diff_rb = compose_colors(image, (1, 0, -1))
    diff_bg = compose_colors(image, (0, 1, -1))
    difference = cv2.merge([diff_rg, diff_rb, diff_bg])
    result = compose_colors(difference, weights)
    return result


def get_edges(image, gauss, thresh1, thresh2):
    # --- Method information ---
    # get_edges returns a map of the edges found in the image
    #
    # --- Inputs ---
    #   image   : Numpy array, 1D image to be processed
    #   gauss   : Odd integer, used to specify the size of the kernel used by GaussianBlur method
    #   thresh1 : Integer, first threshold in the Canny method
    #   thresh2 : Integer, second threshold in the Canny method
    #
    # --- Outputs ---
    #   edges   : Numpy array of the size of the original image, filled with 0s and 1s, where 1 is an edge

    # Apply small Gaussian blur to reduce noise
    image_blur = cv2.GaussianBlur(image, (gauss, gauss), 0, 0)
    # Use canny method for edge detection
    edges = cv2.Canny(image_blur, thresh1, thresh2)
    # Normalize values of the image for later treatment
    # Edge pixels should have a value of 1, non-edge pixels should have value 0
    edges = normalize_image(edges)
    return edges


def obtain_picture(image, center, radius, factor):
    # --- Method information ---
    # obtain_picture returns a picture from an image, specified by the location of a center, the radius of a circle
    # centered on that center, and a factor by which to scale the size of the picture
    #
    # --- Inputs ---
    #   image   : Numpy array, 1D image to be processed
    #   center  : Point object, center of a circle to return from the image
    #   radius  : Float, radius of the circle
    #   factor  : Float, factor by which to scale the size of the returned picture, if possible
    #
    # --- Outputs ---
    #   grid            : Numpy array of the returned picture
    #   circle_center   : Point object, location of the center of the circle in the returned picture
    #   corner          : Point object, location of the top left corner of the returned picture in the image

    # Get image size
    image_size = np.shape(image)
    # Calculate the half of the dimensions of the grid that will be sent for finding edges
    grid_half_size = round(factor * radius)
    # Correct the size of the grid in case borders are not part of the image
    min_x = int(min(max(0, center.x - grid_half_size), image_size[0]))
    max_x = int(min(max(0, center.x + grid_half_size), image_size[0]))
    min_y = int(min(max(0, center.y - grid_half_size), image_size[1]))
    max_y = int(min(max(0, center.y + grid_half_size), image_size[1]))
    # Translate the location of the center of the circle to account for above correction
    circle_center = Point(center.x - min_x, center.y - min_y)
    # Get top left corner for translation purposes
    corner = Point(min_x, min_y)

    image_copy = image.copy()
    grid = image_copy[min_x:max_x, min_y:max_y]

    return grid, circle_center, corner


def preprocess(image_rgb, para):
    # --- Method information ---
    # preprocess processes the RGB image according to specified search settings
    #
    # --- Inputs ---
    #   image_rgb   : Numpy array, RGB image to be preprocessed
    #   para        : Search object
    #
    # --- Outputs ---
    #   image           : Numpy array of the returned picture
    #   img             : Numpy array of the rescaled returned picture
    #   scale_factor    : Float, factor by which img is scaled

    # Obtain the color differences if specified in function
    if para.use_color_differences:
        # Downscale image if necessary, to improve computation time.
        image = get_color_differences(image_rgb, para.color_weights)
        img, scale_factor = rescale_image(image, para.match_para.max_dim)
    else:
        # Convert to grayscale and downscale image if necessary, to improve computation time.
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        img, scale_factor = rescale_image(image, para.match_para.max_dim)

    return image, img, scale_factor


def find_matches(image, img, edg, scale_factor, particles_list, para, use_found_particle):
    # --- Method information ---
    # find_matches finds all the points of the image that possibly correspond to the center of a particle
    #
    # --- Inputs ---
    #   image               : Numpy array, image
    #   img                 : Numpy array, rescaled image
    #   edg                 : Numpy array, edges map of the rescaled image
    #   scale_factor        : Float, factor by which img is scaled
    #   particles_list      : List of particle objects that have previously been found during the search
    #   para                : Search object containing the search settings
    #   use_found_particle  : Specify whether to use a previously found particle for the matching method
    #
    # --- Outputs ---
    #   maxima  : List of point objects corresponding to potential matches

    # Set search parameters in sorter variables for convenience
    radius = para.searched_radius
    factor = para.match_para.factor

    if use_found_particle and len(particles_list) > 0:
        # Get the best particle in particles_list (based on circularity)
        # NOTE : A potential change would be to choose a random particle from the list, as to ensure some
        # variability in the searches. This could help to find particles that are too different from the 'best',
        # but would remove the repeatability of the algorythm.
        best_circularity = 0
        for particle in particles_list:
            if particle.circularity > best_circularity:
                picture, circle_center, picture_corner = obtain_picture(image, particle.center, particle.radius, factor)
                picture = resize_image(picture, scale_factor)
                best_circularity = particle.circularity
        # Use the best particle in the image as a mask for finding the other ones
        object_mask = picture
        threshold = 0.4
        # Compare actual image (scaled down) to object mask
        matches = match_template_full(img, object_mask)

    else:
        diameter = int(2 * radius * scale_factor)
        # Create circle mask for comparison
        mask_size = (round(factor * diameter), round(factor * diameter))
        circle_size = (diameter, diameter)
        object_mask = create_ellipse(mask_size, circle_size, para.match_para.sharpness)
        # Get threshold comparison with near perfect circle
        perfect_circle = create_ellipse(mask_size, circle_size, 1)
        threshold = match_template(perfect_circle, object_mask)
        # Compare edges map to circle template
        matches = match_template_full(edg, object_mask)

    # Use an optimisation method to find significant maxima in the downscaled image and rescale those points
    maxima = find_local_maxima(matches, 10, para.match_para.tolerance * threshold)
    maxima = scale_points(maxima, Point(1 / scale_factor, 1 / scale_factor), do_round=True)

    return maxima


def remove_outliers(particle, thresh):
    # --- Method information ---
    # remove_outliers removes the outlier points of a particle's contour based on statistical analysis
    #
    # --- Inputs ---
    #   particle    : Particle object
    #   thresh      : Float, value to specify the threshold for which a value is considered an outlier
    #
    # --- Outputs ---
    #   particle    : Particle object with refined contour

    r = get_radial_average(particle.contour)
    sd = get_radial_standard_deviation(particle.contour)
    outliers = get_outliers(particle.contour, r, sd, thresh=thresh)
    for index in reversed(outliers):
        particle.contour.pop(index)
    return particle


def analyse(image_rgb, particles_list, para):
    # --- Method information ---
    # analyse attempts to find all the particles of a given size in an image, according to the search parameters
    # entered. The list of particles for this image is then updated with the new particles
    #
    # --- Inputs ---
    #   image_rgb       : Numpy array, RGB image in which to find the particles
    #   particles_list  : List of particle objects to be filled, must only contain particles of the image processed
    #   para            : Search object, containing the search settings
    #
    # --- Outputs ---
    #   particles_list  : List of found particle objects

    # Set search parameters in sorter variables for convenience
    radius = para.searched_radius
    factor = para.match_para.factor
    n = para.iterations + 1

    # Print to terminal
    print(f'Pre-processing image')
    # Convert image to usable format
    image, img, scale_factor = preprocess(image_rgb, para)

    # Obtain edges map at full scale and rescaled
    edges = get_edges(image, para.edges_para.gauss_1, para.edges_para.thresh1_1, para.edges_para.thresh2_1)
    edg = get_edges(img, para.edges_para.gauss_2, para.edges_para.thresh1_2, para.edges_para.thresh2_2)
    # Also obtain an edges map with as much information as possible
    # This is relevant when the use_color_differences option is set to true : edges_max is produced without using
    # this parameter, thus conserving more detail. This helps when constructing the contours.
    image_max = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    edges_max = get_edges(image_max, para.edges_para.gauss_1, para.edges_para.thresh1_1, para.edges_para.thresh2_1)

    # Proceed to n searches. This corresponds to a preliminary search using only the edges maps for object
    # detection, then the amount of iterations specified for the complete search.
    # For the method to work, the first search has to be successful in finding at least one valid particle.
    # ---
    # Alternatively, the method could be fed with an example particle in particles_list, but this particle would
    # have to be removed from the list upon finding the first valid particle of the image.
    # This removal action is currently not implemented in the code.
    for i in range(0, n):
        if i == 0:
            # Set the condition for the preliminary search and inform the user in the terminal
            print('Proceeding with preliminary search')
            print('...')
            use_found_particle = False
        else:
            # Set the conditions for the latter searches and inform the user in the terminal
            if len(particles_list) == 0:
                # In this case, the function will not find any more particles
                break
            else:
                print(f'Proceeding with iteration {i} out of {n-1}')
                print('...')
                use_found_particle = True

        # Find points potentially corresponding to the centers of particles
        # These points correspond to local maxima from an optimisation standpoint
        maxima = find_matches(image, img, edg, scale_factor, particles_list, para, use_found_particle)

        # Loop through every maximum detected and construct the contour of a disc of the specified radius
        for maximum in maxima:
            # Provide the option to proceed twice, in the case where use_color_differences is set to True.
            for j in range(0, 2):
                if j == 0:
                    use_edges = edges
                else:
                    use_edges = edges_max
                    # This step is redundant if color differences are not used
                    if not para.use_color_differences:
                        break

                # From the location of the maximum found, create an ordered list of point objects corresponding to a
                # potential contour of what could be a particle centered on this location
                picture, circle_center, corner = obtain_picture(use_edges, maximum, radius, factor)
                contour, _ = detect_circle_edge_points(picture, circle_center, radius, para)
                contour = translate_points(contour, corner)

                # Append particle to list if valid
                particle = Particle(contour)
                particles_list, added_particle = append_particle(particles_list, particle, para)
                if added_particle:
                    print(f'Found a particle with c={particle.circularity} and N={len(particle.contour)}')

                # Attempt to refine the contour
                particle = remove_outliers(particle, thresh=2.5)
                particles_list, adjusted_particle = append_particle(particles_list, particle, para)
                if adjusted_particle:
                    print(f'Adjusted particle with c={particle.circularity} and N={len(particle.contour)}')

    return particles_list



