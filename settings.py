global do_run_search


class EdgesParameters:
    def __init__(self):
        self.gauss_1 = 11       # Non-negative odd integer, strength of Gaussian blur of large image
        self.gauss_2 = 3        # Non-negative odd integer, strength of Gaussian blur of downsized image
        self.thresh1_1 = 0      # Non-negative integer, threshold1 in Canny method for large image
        self.thresh2_1 = 50     # Non-negative integer, threshold2 in Canny method for large image
        self.thresh1_2 = 0      # Non-negative integer, threshold1 in Canny method for downsized image
        self.thresh2_2 = 250    # Non-negative integer, threshold2 in Canny method for downsized image


class MatchParameters:
    def __init__(self):
        # NOTE : on sharpness and tolerances, a value of 1 is high and a value of 0 is low
        self.sharpness = 0.7    # Float [0, 1], sharpness of the circle generated for preliminary search in analyse()
        self.tolerance = 0.8    # Float [0, 1], tolerance applied on the threshold for finding maxima in find_matches()
        self.factor = 1.2       # Float, factor by which to scale the size of the picture in obtain_picture()
        self.max_dim = 1080     # Integer, specifies the size for which an image should be resized in preprocess()


class ContourParameters:
    def __init__(self):
        # NOTE : on sharpness and tolerances, a value of 1 is high and a value of 0 is low
        self.nb_points = 35     # Integer greater than 2, number of points to aim for when constructing the contour
        self.dist_tol = 0.8     # Float, tolerance on the overlap of two particles in an image
        self.circ_tol = 0.9     # Float [0, 1], tolerance on the circularity of a new particle
        self.sharpness = 0.7    # Float [0, 1], sharpness of the circle generated used in detect_circle_edge_points()
        self.radial_tol = 0.5   # Float [0, 1], tolerance on accepting a point in find_radial_edge()
        self.nb_tol = 0.8       # Float [0, 1], tolerance on the number of points in the contour vs nb_points


class Search:
    def __init__(self, r, n, use_color_differences):
        self.searched_radius = r                            # Specified radius (in pixels) of the particles to look for
        self.iterations = n                                 # Number of search iterations (besides preliminary search)
        self.use_color_differences = use_color_differences  # Boolean variable, rather self-explanatory
        self.color_weights = [1.0, 1.0, 1.0]                # Weights to use when use_color_differences is set to True
        self.match_para = MatchParameters()
        self.contour_para = ContourParameters()
        self.edges_para = EdgesParameters()


def init():
    # Functional global variable, sadly necessary for the gui (or at least I do not know how to do it differently)
    global do_run_search
    do_run_search = True


