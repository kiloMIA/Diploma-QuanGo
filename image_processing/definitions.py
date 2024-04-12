# Constants
COLOR_WHITE = (255, 255, 255)     # white
COLOR_BLACK = (0, 0, 0)           # black
COLOR_RED = (0, 0, 255)           # red
COLOR_BLUE = (255, 0, 0)          # blue
DEF_IMG_SIZE = (500, 500)         # default shape for board generation
MIN_EDGE_DIST = 2                 # minimum board area distance from edge
DEF_IMG_COLOR = (80, 145, 210)    # default generated board color
DEF_BOARD_SIZE = 19               # default board size
DEF_AVAIL_SIZES = [9, 13, 19]     # available standard board sizes
MAX_BOARD_SIZE = 21               # maximum board size
CV_HEIGTH = 0                     # index of height dimension of OpenCv image
CV_WIDTH = 1                      # index of width dimension of OpenCv image
CV_CHANNEL = 2                    # index of channel dimension of OpenCv image
GR_X = 0                          # index of X coordinate dimension
GR_Y = 1                          # index of Y coordinate dimension
GR_A = 2                          # index of horizontal board position dimension
GR_B = 3                          # index of vertical board position dimension
GR_R = 4                          # index of stone radius dimension
GR_BW = 5                         # index of stone color dimension in board.all_stones
GR_FROM = 0                       # index of line start in lines array
GR_TO = 1                         # index of line end in lines array
STONE_BLACK = 'B'                 # key for black stones
STONE_WHITE = 'W'                 # key for white stones
STONE_COLORS = {STONE_BLACK: "Black", STONE_WHITE: "White"} # stone color names

board_params = {
    'CANNY_MINVAL': 50,
    'CANNY_MAXVAL': 150,
    'CANNY_APERTURE': 3,
    'HL_RHO': 1,
    'HL_THETA': 1,
    'HL_THRESHOLD': 80,
    'HL_MINLEN': 50,
    'HL_RHO2': 2,
    'HL_THETA2': 1,
    'HL_THRESHOLD2': 90,
    'BOARD_SIZE': 19,
    'PYRAMID_B': 1, 
    'PYRAMID_W': 1,
    'STONES_THRESHOLD_B': 84,
    'STONES_THRESHOLD_W': 173,
    'STONES_MAXVAL_B': 255,
    'STONES_MAXVAL_W': 255,
    'HC_MINDIST': 1,        
    'HC_MAXRADIUS': 20,    
    'HC_SENSITIVITY_B': 10, 
    'HC_SENSITIVITY_W': 10, 
    'HC_MASK_B': 3,         
    'HC_MASK_W': 3,         
    'BLUR_MASK_B': 0,      
    'BLUR_MASK_W': 0,     
    'STONES_DILATE_B': 1,
    'STONES_DILATE_W': 1,
    'STONES_ERODE_B': 1,
    'STONES_ERODE_W': 0,
    'WATERSHED_B': 85, 
    'WATERSHED_W': 131,
    'WS_MORPH_B': 0,  
    'WS_MORPH_W': 0, 
    'LUM_EQ': 0,
}


# Analysis results
GR_STONES_B = "BS"                  # black stones
GR_STONES_W = "WS"                  # white stones
GR_BOARD_SIZE = "BOARD_SIZE"        # board size
GR_IMG_GRAY = "IMG_GRAY"            # grayed out image
GR_IMG_BLUE = "IMG_CHANNEL_B"       # blue channel of the image
GR_IMG_RED = "IMG_CHANNEL_R"        # red channel of the image
GR_IMG_THRESH_B = "IMG_THRESH_B"    # thresholded black stones image
GR_IMG_THRESH_W = "IMG_THRESH_W"    # thresholded white stones image
GR_IMG_MORPH_B = "IMG_MORPH_B"      # morthed black stones image
GR_IMG_MORPH_W = "IMG_MORPH_W"      # thresholded white stones image
GR_IMG_LINES = "IMG_LINES1"         # generated lines image for 1st pass
GR_IMG_LINES2 = "IMG_LINES2"        # generated lines image for 2nd pass
GR_IMG_EDGES = "IMG_EDGES"          # edges image
GR_EDGES = "EDGES"                  # edges array (x,y), (x,y)
GR_SPACING = "SPACES"               # spacing of board net (x,y)
GR_NUM_LINES = "NLIN"               # overall number of lines found
GR_NUM_CROSS_H = "NCROSS_H"         # Number of crosses on horizontal line
GR_NUM_CROSS_W = "NCROSS_W"         # Number of crosses on vertical line
GR_IMAGE_SIZE = "IMAGE_SIZE"        # Image size (width, height)
GR_IMG_WS_B = "IMG_WATERSHED_B"     # Watershed black stones image
GR_IMG_WS_W = "IMG_WATERSHED_W"     # Watershed white stones image
