"""
Initialize global variables
"""
from PyQt5.QtGui import QFont

# Pandas input file path in string type
datafile = "Resources/data.xlsx"

# Network
port = 5555 # Do not use a low number as these ports often are used for specific things
BUFFER_SIZE = 4096 # Do not use a too low buffer size (< 1kb).

# Initial values
initialPlantPrice = 1000
default_years = 5
default_rounds = 2
default_money = 1000  # Recommended: 1000 (1000 mill)

# Colors
darkmode = True
darkmode_background_color = [0.20784, 0.20784, 0.20784]
darkmode_background_color_styleSheet = "rgb(53, 53, 53)"
darkmode_light_dark_color = [0.2588, 0.2588, 0.2588]
darkmode_light_dark_color_styleSheet = "rgb(66, 66, 66)"
darkmode_light_styleSheet = "rgb(80, 80, 80)"
darkmode_color_white = [1,1,1]
darkmode_color_white_styleSheet = "rgb(255,255,255)"
darkmode_color_red = [1, 0.16, 0]
darkmode_color_red_styleSheet = "rgb(255, 40.8, 0)"
darkmode_color_green = [0.14901, 0.47843, 0.10588]
darkmode_color_green_styleSheet = "rgb(38, 122, 27)"
darkmode_color_disabled_green = [0.1686, 0.25098, 0.1686]
darkmode_color_disabled_green_styleSheet = "rgb(43, 64, 43)"
lightmode_color_background_styleSheet = "rgb(240, 240, 240)"

standard_color_scheme = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan", "darkblue", "gold", "limegreen", "salmon", "purple", "saddlebrown", "fuchsia", "darkgrey", "olivedrab", "dodgerblue"]

# Fonts

# High font size fonts
title_font_big = QFont()
title_font_big.setPointSize(18)
big_text_font_big = QFont()
big_text_font_big.setPointSize(24)
small_text_font_big = QFont()
small_text_font_big.setPointSize(18)
tiny_text_font_big = QFont()
tiny_text_font_big.setPointSize(12)
huge_text_font_big = QFont()
huge_text_font_big.setPointSize(36)
giant_text_font_big = QFont()
giant_text_font_big.setPointSize(200)
radiobutton_width_big = "36"
radiobutton_height_big = "36"

# Medium font size fonts
title_font_mid = QFont()
title_font_mid.setPointSize(16)
big_text_font_mid = QFont()
big_text_font_mid.setPointSize(18)
small_text_font_mid = QFont()
small_text_font_mid.setPointSize(14)
tiny_text_font_mid = QFont()
tiny_text_font_mid.setPointSize(12)
huge_text_font_mid = QFont()
huge_text_font_mid.setPointSize(28)
giant_text_font_mid = QFont()
giant_text_font_mid.setPointSize(164)
radiobutton_width_mid = "30"
radiobutton_height_mid = "30"

# Low font size fonts recommended for low resolution displays
title_font_small = QFont()
title_font_small.setPointSize(9)
big_text_font_small = QFont()
big_text_font_small.setPointSize(12)
small_text_font_small = QFont()
small_text_font_small.setPointSize(10)
tiny_text_font_small = QFont()
tiny_text_font_small.setPointSize(8)
huge_text_font_small = QFont()
huge_text_font_small.setPointSize(18)
giant_text_font_small = QFont()
giant_text_font_small.setPointSize(100)
radiobutton_width_small = "24"
radiobutton_height_small = "24"

high_font_settings = {"title": title_font_big,"big_text": big_text_font_big, "small_text": small_text_font_big, "tiny_text": tiny_text_font_big, "huge_text": huge_text_font_big, "giant_text": giant_text_font_big, "radiobutton_height": radiobutton_height_big, "radiobutton_width": radiobutton_width_big}
mid_font_settings = {"title": title_font_mid,"big_text": big_text_font_mid, "small_text": small_text_font_mid, "tiny_text": tiny_text_font_mid, "huge_text": huge_text_font_mid, "giant_text": giant_text_font_mid, "radiobutton_height": radiobutton_height_mid, "radiobutton_width": radiobutton_width_mid}
low_font_settings = {"title": title_font_small,"big_text": big_text_font_small, "small_text": small_text_font_small, "tiny_text": tiny_text_font_small, "huge_text": huge_text_font_small, "giant_text": giant_text_font_small, "radiobutton_height": radiobutton_height_small, "radiobutton_width": radiobutton_width_small}
fonts = {"big": high_font_settings, "mid": mid_font_settings, "small": low_font_settings}

# Misc
app = None # Used for theme
standard_palette = None # Used for theme
warningTimer = 3  # seconds. Seconds a warning message is shown for the player. Recommended: 3
DEBUGGING = True # Used to show detailed progress information and exceptions in the log
