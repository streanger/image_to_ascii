#!/usr/bin/python3
import sys
import os
import math
import time
import numpy as np
from PIL import Image
from termcolor import colored


def script_path():
    current_path = os.path.realpath(os.path.dirname(sys.argv[0]))
    os.chdir(current_path)
    return current_path
    
    
def timer(func):
    def f(*args, **kwargs):
        before = time.time()
        val = func(*args, **kwargs)
        after = time.time()
        print("[*]elapsed time: {}[s] ({})".format(after-before, func.__name__))
        return val
    return f
    
    
def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])
    
    
def open_image(filename):
    img = Image.open(filename)
    return img
    
    
def write_file(filename, text, mode='w'):
    '''write to file'''
    try:
        with open(filename, mode, encoding='utf-8') as f:
            f.write(text)
    except Exception as err:
        print('[x] failed to write to file: {}, err: {}'.format(filename, err))
    return None
    
    
def ascii_list(key):
    '''works as color map for image -> ascii convertion
    key=2 seems to be the most acurate
    '''
    my_map = [' ',' ','.','`',',','-','-','~','"','^','*',';','i','l','=','v','x','C','P','G','&','$','O','Q','@','@','X','X','#','#',chr(0x25a0),chr(0x25a0)]   #32
    my_map = "".join([item*8 for item in my_map])
    my_map = my_map[::-1]
    
    data = {
        1: my_map,
        
        # 'https://ascii-generator.site/'
        2: '@@@@@@@@@@@@@@@@@@@@@@@@@@%%%%%%%%%%%%%%%%%%%%%%%%%##########################*************************++++++++++++++++++++++++++=========================--------------------------:::::::::::::::::::::::::..........................                          ',
        
        # 'https://manytools.org/hacker-tools/convert-images-to-ascii-art/go/'
        3: '@@@@@@@@@@@@@@@@@@@@@@@@@@@@&&&&&&&&&&&&&&&&&&&&&&&&%%%%%%%%%%%%%%%%%%%%%%%%%%##########################((((((((((((((((((((((((((////////////////////////**************************,,,,,,,,,,,,,,,,,,,,,,,,,,..........................                        ',
        
        # 'https://www.text-image.com/convert/pic2ascii.cgi'
        4: 'MMMMMMMMMMNNNNNNNNNNNNNNNNNNmmmmmmmmmmmmmmmmmmddddddddddddddddddhhhhhhhhhhhhhhhhhhyyyyyyyyyyyyyyyyyyyssssssssssssssssssoooooooooooooooooo++++++++++++++++++///////////////////::::::::::::::::::------------------..................``````````````````          ',
        
        # 'https://www.ascii-art-generator.org/'
        5: "MMMMMMWWWWWWWWWWWNNNNNNNNNNNNXXXXXXXXXXXXKKKKKKKKKKK000000000000OOOOOOOOOOOkkkkkkkkkkkkxxxxxxxxxxxxdddddddddddoooooooooooollllllllllllcccccccccccc:::::::::::;;;;;;;;;;;;,,,,,,,,,,,,'''''''''''...................................                             ",
    }
    if not key in range(1, 6):
        key = 1
    return list(data[key])
    
    
# @timer
def image_to_ascii(filename, target_width=100, reverse=True, colorized=True, mapping_key=1):
    """
    target_width - ascii image width in characters
    reverse - reverse colors flag
    """
    img = open_image(filename)      # PIL format
    
    # ********* resize due to wrong width/height ratio in terminal/notepad *********
    init_width, init_height = img.size
    # width_compensation_ratio = 1.8   # npp
    width_compensation_ratio = 2.1     # python terminal
    new_width = round(init_width*width_compensation_ratio)
    img = img.resize((new_width, init_height))
    
    # ********* resize *********
    target_height = round((target_width/new_width)*init_height)
    # print('target size: ({}, {})'.format(target_width, target_height))
    img = img.resize((target_width, target_height))
    
    # ********* convert to numpy array & remove alpha channel *********
    img = np.array(img, dtype=np.uint8)     # PIL -> numpy
    img = img[:, :, :3]                     # remove alpha channel;
    
    # ********* convert to gray *********
    gray = rgb2gray(img)
    
    # ********* round to int *********
    rounded = np.rint(gray).astype(int)
    
    # ********* colors map *********
    if colorized:
        data = termcolor_colors()
        termcolor_xyz = [rgb_to_xyz(*val) for key, val in data.items()]
        # termcolor_xyz_rgb = {rgb_to_xyz(*val): val for key, val in data.items()}  # may be used for creating image
        termcolor_xyz_name = {rgb_to_xyz(*val): key for key, val in data.items()}
        colors_map = [[termcolor_xyz_name[closest_point(termcolor_xyz, rgb_to_xyz(*px))] for px in row] for row in img.tolist()]
        
    # ********* convert to ascii *********
    ascii_map = ascii_list(mapping_key)    # list with index access (consider dict)
    if reverse:
        ascii_map.reverse()
    img_rows = rounded.tolist()
    if colorized:
        ascii_image = '\n'.join([''.join([colored(ascii_map[item], colors_map[x][y]) for y, item in enumerate(row)]) for x, row in enumerate(img_rows)])
    else:
        ascii_image = '\n'.join([''.join([ascii_map[item] for y, item in enumerate(row)]) for x, row in enumerate(img_rows)])
    return ascii_image
    
    
def rgb_to_xyz(r, g, b):
    '''red - 0deg, green - 120deg, blue - 240deg'''
    r_vector = np.array([r, 0, r])
    g_vector = np.array([math.cos((120/360)*2*math.pi)*g, math.sin((120/360)*2*math.pi)*g, g])
    b_vector = np.array([math.cos((240/360)*2*math.pi)*b, math.sin((240/360)*2*math.pi)*b, b])
    
    out = r_vector + g_vector + b_vector
    out = tuple(int(round(item)) for item in out)
    return out
    
    
def calculate_distance_xyz(x1, y1, z1, x2, y2, z2):
    '''ok for now'''
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return dist
    
    
def termcolor_colors():
    """termcolor colors mapping"""
    data = {
        'red': (197, 15, 31),
        'green': (19, 161, 14),
        'yellow': (193, 156, 0),
        'blue': (0, 55, 218),
        'magenta': (136, 23, 152),
        'cyan': (58, 150, 221),
        'white': (204, 204, 204),
    }
    return data
    
    
def closest_point(points, single):
    """match single point to the closest from the points list; coords are x, y
    -that won't work as i thought, because of ignoring amplitude e.g. (0, 0, 0) is equal to (255, 255, 255)
    """
    distances = []
    for point in points:
        dist = calculate_distance_xyz(*point, *single)
        distances.append((point, dist))
        
    closest = sorted(distances, key=lambda x: x[1])[0]  # get first item
    color = closest[0]
    return color
    
    
def colors_mapping_example():
    """map full range colors (0-255, RGB) to termcolor colors"""
    colors = [
        (50, 50, 50),
        (50, 150, 200),
        (200, 100, 10),
        (200, 0, 200),
        (0, 100, 0),
        (100, 0, 0),
        (200, 200, 150),
    ]
    
    # ********* colors mapping *********
    data = termcolor_colors()
    termcolor_xyz = [rgb_to_xyz(*val) for key, val in data.items()]
    termcolor_xyz_rgb = {rgb_to_xyz(*val): val for key, val in data.items()}
    termcolor_xyz_name = {rgb_to_xyz(*val): key for key, val in data.items()}
    
    for px in colors:
        single_xyz = rgb_to_xyz(*px)
        out = closest_point(termcolor_xyz, single_xyz)
        converted = termcolor_xyz_rgb[out]
        color_name = termcolor_xyz_name[out]
        print('{} -> {} -> {}'.format(px, color_name, converted))
    return None
    
    
if __name__ == "__main__":
    script_path()
    os.system('color')
    
    args = sys.argv[1:]
    if not args:
        print(colored('[x] please specify image as argument', 'yellow'))
        print(colored('[*] example command:', 'cyan'))
        print(colored('    python image_to_ascii.py image.png', 'cyan'))
        sys.exit()
    filename = args[0]
    ascii_image = image_to_ascii(filename, target_width=200, reverse=True, colorized=True, mapping_key=3)
    print(ascii_image)
    # write_file('image.txt', ascii_image)
    
    
'''
useful:
    https://stackoverflow.com/questions/35902302/discarding-alpha-channel-from-images-stored-as-numpy-arrays
    https://www.kite.com/python/answers/how-to-convert-an-image-from-rgb-to-grayscale-in-python
'''