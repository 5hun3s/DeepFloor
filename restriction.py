import random
import math

def set_alongwall_dir_ctr(v_width, min_x, max_x, min_y, max_y, delta=0.01):
    rand = random.choice([0, 1, 2, 3])
    if rand == 0:
        x, y, rotation = random.uniform(min_x + v_width, max_x), min_y + delta, 90
    elif rand == 1:
        x, y, rotation = max_x - delta, random.uniform(min_y+v_width, max_y), 180
    elif rand == 2:
        x, y, rotation = random.uniform(min_x, max_x-v_width), max_x - delta, 270 
    elif rand == 3:
        x, y, rotation = min_x + delta, random.uniform(min_y ,max_y-v_width), 0
    return x, y, rotation

def set_alongwall(min_x, max_x, min_y, max_y, rand_rotation, delta=0.01):
    rand = random.choice([0, 1])
    rotation = random.choice(rand_rotation)
    if rand == 0:
        x, y = random.choice([min_x + delta, max_x - delta]), random.uniform(min_y, max_y)
    elif rand == 1:
        x, y = random.uniform(min_x, max_x), random.choice([min_y + delta, max_y - delta])
    return x, y, rotation

def set_combo(v_width, h_width, min_x, max_x, min_y, max_y, set_furniture=None, delta=0.01):
    """家具の配置の際に特定の家具とセットでおかれるようにする
    Parameters
    ---------
    - set_furniture : dict
        セットでおく家具の情報が入った辞書オブジェクト
    - rand_rotation : 一緒におく家具がない場合の解き様
    """
    set_f_x, set_f_y, set_f_rotation = set_furniture["x"] + delta*math.sin(math.radians(set_furniture["rotation"])), set_furniture["y"] - delta*math.cos(math.radians(set_furniture["rotation"])), set_furniture["rotation"]
    rand = random.choice([0, 1, 2, 3]) 
    if rand == 0:
        set_f_rand_len = random.uniform(0, set_furniture["h_width"] - v_width)
        x = set_f_x + set_f_rand_len*math.cos(math.radians(set_f_rotation)) + v_width*math.cos(math.radians(set_f_rotation)) + h_width*math.sin(math.radians(set_f_rotation))
        y = set_f_y + set_f_rand_len*math.sin(math.radians(set_f_rotation)) + v_width*math.sin(math.radians(set_f_rotation)) - h_width*math.cos(math.radians(set_f_rotation))
        rotation = set_f_rotation + 90
    elif rand == 1:
        set_f_rand_len = random.uniform(0, set_furniture["v_width"] - v_width)
        x = set_f_x + set_furniture["h_width"]*math.cos(math.radians(set_f_rotation)) - set_f_rand_len*math.sin(math.radians(set_f_rotation)) + h_width*math.cos(math.radians(set_f_rotation)) - v_width*math.sin(math.radians(set_f_rotation))
        y = set_f_y + set_furniture["h_width"]*math.sin(math.radians(set_f_rotation)) + set_f_rand_len*math.cos(math.radians(set_f_rotation)) + h_width*math.sin(math.radians(set_f_rotation)) + v_width*math.cos(math.radians(set_f_rotation))
        rotation = set_f_rotation + 180
    elif rand == 2:
        set_f_rand_len = random.uniform(0, set_furniture["h_width"] - v_width)
        x = set_f_x + set_f_rand_len*math.cos(math.radians(set_f_rotation)) - h_width*math.sin(math.radians(set_f_rotation)) - set_furniture["v_width"]*math.sin(math.radians(set_f_rotation))
        y = set_f_y + set_f_rand_len*math.sin(math.radians(set_f_rotation)) + h_width*math.cos(math.radians(set_f_rotation)) + set_furniture["v_width"]*math.cos(math.radians(set_f_rotation))
        rotation = set_f_rotation - 90
    elif rand == 3:
        set_f_rand_len = random.uniform(0, set_furniture["v_width"] - v_width)
        x = -1*set_f_rand_len*math.sin(math.radians(set_f_rotation)) - h_width*math.cos(math.radians(set_f_rotation))
        y = set_f_rand_len*math.cos(math.radians(set_f_rotation)) - h_width*math.sin(math.radians(set_f_rotation))
        rotation = set_f_rotation
    return x, y, rotation

def set_facing(v_width, h_width, min_x, max_x, min_y, max_y, face_furniture, delta=0.01):
    """家具配置の際に特定の家具と向かい合いになるように配置するための関数
    """
    face_rotation = face_furniture["rotation"]
    face_x, face_y, face_h, face_v = face_furniture["x"], face_furniture["y"], face_furniture["h_width"], face_furniture["v_width"]
    if face_rotation == 0:
        x, y, rotation = random.uniform(face_x+h_width+face_h, max_x), face_y + face_v/2 + v_width/2, 180
    elif face_rotation == 90:
        x, y, rotation = face_x - face_v/2 - v_width/2, random.uniform(face_y+h_width+face_h, max_y), 270
    elif face_rotation == 180:
        x, y, rotation = random.uniform(min_x, face_x-face_h-h_width), face_y - face_v/2 - v_width/2, 0
    elif face_rotation == 270:
        x, y, rotation = face_x + face_v/2 + v_width/2, random.uniform(min_y ,face_y-h_width-face_h), 90
    return x, y, rotation

        
