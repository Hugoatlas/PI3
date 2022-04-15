import cv2
import export
import gui
import settings

from analyseContour import append_particle, Particle, get_radial_standard_deviation
from analyseImage import analyse
from classes import Point
from constructContour import scale_points


def search():
    for i in range(0, len(image_src_list)):
        print(f'Starting search on image "{image_src_list[i]}". ({i + 1} / {len(image_src_list)})')
        # Load image and convert to grayscale
        image_bgr = cv2.imread(image_src_list[i])
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        image_list.append(image_rgb)

        # Initialize the list of particles to be found in the loaded image
        particles_img = []

        for j in range(0, len(search_settings_list)):
            # Initialize the particles list for this search in the image
            particles = []
            print(f'Looking for particles with r={search_settings_list[j].searched_radius}')

            particles = analyse(image_rgb, particles, search_settings_list[j])

            print(f'Found {len(particles)} particles.')
            print('')

            for particle in particles:
                # Add particle object particles list of this image, if particle is valid
                particles_img, _ = append_particle(particles_img, particle, search_settings_list[j])

        particles_list.append(particles_img)

    # Get the average radius of all the particles in calibration images
    particle_count = 0
    sum_of_radii = 0
    for index in calibration_image_index:
        if 0 <= index < len(particles_list):
            for particle in particles_list[index]:
                particle_count += 1
                sum_of_radii += particle.radius

    # Get pixel to unit conversion
    if particle_count != 0:
        average_radius = sum_of_radii / particle_count
        pixel_to_unit = calibration_particle_radius / average_radius
    else:
        pixel_to_unit = 1

    for i in range(0, len(particles_list)):
        print(f'In image {i + 1}:')
        print(f'{len(particles_list[i])} particles were found')

        for particle in particles_list[i]:
            actual_particle = Particle(scale_points(particle.contour,
                                                    Point(pixel_to_unit, pixel_to_unit), do_round=True))
            r = actual_particle.radius
            c = actual_particle.circularity
            sd = get_radial_standard_deviation(actual_particle.contour)
            pos_x = round(particle.center.x)
            pos_y = round(particle.center.y)
            print(
                f'r = {r}, c = {c}, sd = {sd}'
                f', position : x = {pos_x}, y = {pos_y}')

    # Save data in files
    data = export.convert_particles_data(particles_list)
    export.save_data(data, data_src)
    export.save_particles_to_images(image_list, particles_list, images_src)


settings.init()             # Run this to initiate the do_run_search global variable
particles_list = []         # Initialize the list of particles
image_src_list = []         # Initialize the list image sources
search_settings_list = []   # Initialize the list of search settings
image_list = []             # Initialize the list of images

# -*- USER MANUAL -*-
#
#   1. Tell the program which images you wish to process by listing the filenames of all these images in image_src_list.
#           a. All images used should be similar (view angle, camera set-up, lighting, etc.).
#           b. The pictures should be taken as to limit distortions caused by perspective.
#
#   2. Specify which image/s to use as calibration by entering their index (from image_src_list) in
#      calibration_image_index.
#           a. Calibration images should only contain one type of particle to use as reference.
#           b. These particles must be similar and be of know dimension.
#
#   3. Specify the true radius of the calibration particles in whatever units desired.
#
#   4. Run the program from main, this should open the gui.
#           a. From the gui, you can load, save and modify different search settings.
#              Note that these settings will initially be loaded from the settings.dat file in Current_Search.
#              When saving, replacing or removing search settings in the gui, the settings.dat file will be updated
#              automatically.
#           b. When starting the search from the gui, search_settings_list will be overwritten by the settings saved in
#              the settings.dat file.
#           c. You can open an image from the gui to view the edge detection on this image. You will need to press the
#              Apply button after having opened the image in the gui.
#           d. There are more settings that can be modified directly from the settings.py module.
#
#   5. When the program will be done, all the particles found will be saved as a list of particle objects
#      in the data.dat file in Current_Search.
#
#   If you do not want to use the gui, you can comment out the line where the gui.open_window() is called.
#   Then, you will need to create the search_settings_list yourself by appending and modifying Search objects as
#   shown below.


image_src_list.append('Photos/Air_Soft_1.jpg')
# image_src_list.append('Photos/Air_Soft_2.jpg')
# image_src_list.append('Photos/Verre_Large_1.jpg')
# image_src_list.append('Photos/Verre_Large_2.jpg')
# image_src_list.append('Photos/Verre_Small_1.jpg')

calibration_image_index = [0]
calibration_particle_radius = 100

# Set the settings for all searches
search_settings_list.append(settings.Search(r=135, n=1, use_color_differences=False))
# search_settings_list.append(settings.Search(r=100, n=1, use_color_differences=False))
# search_settings_list.append(settings.Search(r=200, n=3, use_color_differences=True))
# search_settings_list[len(search_settings_list) - 1].color_weights = [1.0, 1.0, 0.0]
# search_settings_list.append(settings.Search(r=160, n=3, use_color_differences=True))
# search_settings_list[len(search_settings_list) - 1].color_weights = [1, 1, 0]
# search_settings_list.append(settings.Search(r=130, n=3, use_color_differences=True))

settings_src = 'Current_Search/settings'
data_src = 'Current_Search/data'
images_src = 'Current_Search/images'
image_src_list, search_settings_list = gui.open_window(image_src_list, settings_src)
# NOTE : To disable the gui, comment the line above and be sure to specify the search settings in
# search_settings_list.

if settings.do_run_search:
    search()
