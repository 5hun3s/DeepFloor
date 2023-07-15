import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon
from shapely.affinity import rotate
from matplotlib.lines import Line2D
from shapely.geometry import LineString
import math
import random
import pandas as pd
import os

def create_rectangle(center, width, height, angle, color):
    rectangle = patches.Rectangle((center[0] - width / 2.0, center[1] - height / 2.0), width, height, angle=angle, fill=False, edgecolor=color)
    rectangle_coordinates = [(center[0] - width / 2.0, center[1] - height / 2.0), 
                             (center[0] - width / 2.0, center[1] + height / 2.0), 
                             (center[0] + width / 2.0, center[1] + height / 2.0), 
                             (center[0] + width / 2.0, center[1] - height / 2.0)]
    rectangle_polygon = Polygon(rectangle_coordinates)
    rectangle_polygon = rotate(rectangle_polygon, angle, origin=(center[0] - width / 2.0, center[1] - height / 2.0))
    return rectangle, rectangle_polygon


def create_line(start, end, color):
    line_polygon = LineString([(start[0], start[1]), (end[0], end[1])])
    line = Line2D([start[0], end[0]], [start[1], end[1]], color=color)
    return line, line_polygon
#chatGPTにより追加
def create_direction_line(center, angle, color):
    end_point = (center[0] + math.cos(math.radians(angle)), center[1] + math.sin(math.radians(angle)))
    line, line_polygon = create_line(center, end_point, color)
    return line, line_polygon

def plot_line(line, ax):
    ax.add_line(line)
    
# 中心を見つける関数
def find_center(points):
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    center_x = sum(x_coords) / len(points)
    center_y = sum(y_coords) / len(points)
    return (center_x, center_y)

# 角度を計算する関数
def calculate_angle(point, center):
    return math.atan2(point[1] - center[1], point[0] - center[0])

# 各点を角度に基づいてソートする関数
def sort_points(points):
    center = find_center(points)
    return sorted(points, key=lambda point: calculate_angle(point, center))

def multi_check_overlap(obj1, objs2):
    for obj in objs2:
        if obj.intersects(obj1):
            return True
        else:
            continue
    return False

class Furniture():
    """家具クラス
    """
    def __init__(self, v_width:float, h_width:float, rotation:int=0, name:str=None, color:str=None):
        self.v_width = v_width
        self.h_width = h_width
        self.rotation = rotation
        self.name = name
        self.color = color

class Room():
    """部屋クラス
    """
    def __init__(self, edges:list, windows:list=None, doors:list=None):
        """
        Parameters
        ----------
        edges : list
            部屋の角の座標(左下を始点に時計周りで記述)[[x座標, y座標], [float, float], ]
        windows : list
            窓の情報[
            {"start":[x座標, y座標], "end":[x座標, y座標]},
            {"start":[x座標, y座標], "end":[x座標, y座標]},
            ]
        doors : list
            ドアの情報[
            {"start":[x座標, y座標], "end":[x座標, y座標]},
            {"start":[x座標, y座標], "end":[x座標, y座標]},,
            ]
        """
        self.edges = edges
        self.windows = windows
        self.doors = doors
        self.line_objects = []
        self.direction_lines = []
        self.furniture_objects = []
        self.furniture_draw_objects = []
        self.furniture_text_objects = []
        
    def plot_room(self, ax):
        """家具を抜きにした部屋と窓、ドアを描画するメソッド
        """
        x_coords = [edge[0] for edge in self.edges]
        y_coords = [edge[1] for edge in self.edges]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        ax.set_xlim([min_x-2, max_x+2])
        ax.set_ylim([min_y-2, max_y+2])
        ax.set_aspect('equal')
        
        points = [lst for lst in self.edges]
        if self.windows!=None:
            wind_starts = [dic["start"] for dic in self.windows]
            wind_ends = [dic["end"] for dic in self.windows]
            points += wind_starts + wind_ends
            winds = wind_starts + wind_ends 
        
        if self.doors!=None:
            door_starts = [dic["start"] for dic in self.doors]
            door_ends = [dic["end"] for dic in self.doors]
            points += door_starts + door_ends
            doors = door_starts + door_ends
            
        
        points = sort_points(points)
        last_ps = [points[-1], points[0]]
        last_line = {"x":[last_ps[0][0], last_ps[1][0]], "y":[last_ps[0][1], last_ps[1][1]]}
        if (self.windows!=None) and (last_ps[0] in winds) and (last_ps[1] in winds):
            last_line["color"] = "blue"
        elif (self.doors!=None) and (last_ps[0] in doors) and (last_ps[1] in doors):
            last_line["color"] = "red"
        else:
            last_line["color"] = "k"
        lines = [
            last_line
        ]
        for i in range(len(points)-1):
            ps = points[i:i+2]
            line = {"x":[ps[0][0], ps[1][0]], "y":[ps[0][1], ps[1][1]]}
            if (self.windows!=None) and (ps[0] in winds) and (ps[1] in winds):
                line["color"] = "blue"
            elif (self.doors!=None) and (ps[0] in doors) and (ps[1] in doors):
                line["color"] = "red"
            else:
                line["color"] = "k"
            lines.append(line)
        for line in lines:
            draw_line, calculate_line = create_line(start=[line["x"][0], line["y"][0]], end=[line["x"][1], line["y"][1]], color=line["color"])
            plot_line(draw_line, ax)
            self.line_objects.append(calculate_line)
        
    def plot_furniture(self, ax, furnitures:list, furnitures_coord:list):
        """家具を配置するメソッド

        Parameters
        ----------
        furnitures : list
            家具オブジェクトが入ったリスト
        furniture_coord : list
            家具オブジェクトの位置が入ったリスト

        Retruns
        ------
        error_flag : list
            配置した家具の状態を表した数字が格納されたリスト(1:壁と重ねっている、2:他の家具に重なっている、0:正常に配置されている)
        """
        error_flag = list()
        x_coords = [edge[0] for edge in self.edges]
        y_coords = [edge[1] for edge in self.edges]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        for furniture, coord in zip(furnitures, furnitures_coord): 
            draw_furniture, calculate_furniture = create_rectangle(coord, furniture.h_width, furniture.v_width, furniture.rotation, furniture.color)
            furniture_name_text = ax.text(coord[0], coord[1], furniture.name, color=furniture.color, fontsize=13) # added this line
            self.furniture_text_objects.append(furniture_name_text) # added this line
            draw_direction, _ = create_direction_line(coord, furniture.rotation, furniture.color) # add this line
            plot_line(draw_direction, ax)#add this line
            self.direction_lines.append(draw_direction)
            if (multi_check_overlap(calculate_furniture, self.line_objects)) or (coord[0]-max([furniture.h_width, furniture.v_width])<min_x) or (coord[0]+max([furniture.h_width, furniture.v_width])>max_x) or (coord[1]-max([furniture.h_width, furniture.v_width])<min_y) or (coord[1]+max([furniture.h_width, furniture.v_width])>max_y):
                error_flag.append(1)
            elif multi_check_overlap(calculate_furniture, self.furniture_objects):
                error_flag.append(2)
            else:
                error_flag.append(0)
           

            ax.add_patch(draw_furniture)
            self.furniture_objects.append(calculate_furniture)
            self.furniture_draw_objects.append(draw_furniture)
        return error_flag

 

    def clear_furniture(self, ax, furniture_index:int=None, all_clear:bool=False):
        """配置した家具を削除するメソッド

        Parameters
        ---------
        furniture_index : int
            削除したい家具のfurnitureにおけるインデックス値
        all_clear : bool
            描画した家具全てを削除するかどうか
        """
        if furniture_index!=None:
            self.furniture_draw_objects[furniture_index].remove()
            self.direction_lines[furniture_index].remove()
            self.furniture_text_objects[furniture_index].remove()
            del self.furniture_objects[furniture_index]
            del self.furniture_draw_objects[furniture_index]
            del self.direction_lines[furniture_index]
            del self.furniture_text_objects[furniture_index]
        if all_clear:
            for i_1,i_2,i_3 in zip(self.furniture_draw_objects, self.direction_lines, self.furniture_text_objects):
                i_1.remove()
                i_2.remove()
                i_3.remove()
            self.furniture_objects = list()
            self.furniture_draw_objects = list()
            self.direction_lines = list()
            self.furniture_text_objects = list()
        
    def random_plot_furniture(self, random_furniture:list, ax):
        x_coords = [edge[0] for edge in self.edges]
        y_coords = [edge[1] for edge in self.edges]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        furniture_info = list()
        for f_dic in random_furniture:
            dic = dict()
            while True:
                #dic["v_width"] = random.randint(f_dic["v_width_range"][0], f_dic["v_width_range"][1])
                #dic["h_width"] = random.randint(f_dic["h_width_range"][0], f_dic["h_width_range"][1])
                #dic["rotation"] = random.choice(f_dic["rotation_range"])
                #dic["name"] = f_dic["name"]
                #dic["color"] = f_dic["color"]
                dic["v_width"] = f_dic["v_width_range"]
                dic["h_width"] = f_dic["h_width_range"]
                dic["rotation"] = random.choice(f_dic["rotation_range"])
                dic["name"] = f_dic["name"]
                dic["color"] = f_dic["color"]
                dic["coord"] = [[random.randint(min_x, max_x), random.randint(min_y, max_y)]]
                furniture = Furniture(dic["v_width"], dic["h_width"], dic["rotation"], f_dic["name"], f_dic["color"])
                error_flag = self.plot_furniture(ax, [furniture], dic["coord"])#ポジションのエラーを追加
                if error_flag[0]!=0:
                    self.clear_furniture(ax, furniture_index=-1)
                elif error_flag[0]==0:
                    furniture_info.append(dic)
                    break
        return furniture_info
    """             
    def make_random(self, random_furniture:list save_path:str, num:int):
        for _ in range(num):
            fig, ax = plt.subplots()
            self.random_plot_furniture(random_furniture, ax)
            fig.savefig(fsasa/save_path)
    """
def main(room_edges:list, random_furniture:list, save_path:str, num:int, windows:list=None, doors:list=None):
    if os.path.isfile(f"""{os.getcwd()}/dataset/room_info.xlsx"""):
        room_info = pd.read_excel(f"""{os.getcwd()}/dataset/room_info.xlsx""", engine="openpyxl")
    else:  # If file does not exist, create a new DataFrame
        room_info = pd.DataFrame()
    image_num = len(os.listdir(f"""{os.getcwd()}/dataset/uninspected""")) + len(os.listdir(f"""{os.getcwd()}/dataset/inspected"""))
    for _ in range(num):
        fig, ax = plt.subplots()
        room = Room(room_edges, windows=windows, doors=doors)
        room.plot_room(ax)
        furniture_info_list = room.random_plot_furniture(random_furniture=furniture_dic, ax=ax)
        for furniture_info in furniture_info_list:
            df = pd.DataFrame(furniture_info)
            df["room"] = f"""room_{str(_ + image_num)}"""
            room_info = pd.concat([room_info, df])
        fig.savefig(f"""{os.getcwd()}/dataset/uninspected/room_{str(_ + image_num)}.png""")
    room_info["target"] = "uninspected"
    return room_info
        
        
        
        
        
if __name__ ==  "__main__":
    #f_1 = Furniture(v_width=2, h_width=3, rotation=45, name="TV", color="red")
    #f_2 = Furniture(v_width=2, h_width=2, rotation=0, name="bed", color="blue")
    edges = [
    [1, 1],
    [1, 10],
    [10, 10],
    [10, 1]
    ]
    winds = [
        {"start":[1,5], "end":[1,6]},
        {"start":[5,10], "end":[6,10]},

    ]
    dors = [
        {"start":[10, 5], "end":[10, 6]}
    ]
    furniture_dic = [
        {"v_width_range":0.5, "h_width_range":1.4, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"sofa", "color":"brown"},
        {"v_width_range":0.6, "h_width_range":1.2, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"desk", "color":"orange"},
        {"v_width_range":0.5, "h_width_range":0.5, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"chair", "color":"red"},
        #{"v_width_range":0.05, "h_width_range":1.2, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"TV", "color":"blue"},
        {"v_width_range":0.4, "h_width_range":1.8, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"TV stand", "color":"navy"},
        {"v_width_range":0.2, "h_width_range":0.2, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"light", "color":"gold"},
        {"v_width_range":0.2, "h_width_range":0.2, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"plant", "color":"green"},
        {"v_width_range":0.3, "h_width_range":0.4, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"shelf", "color":"magenta"},
        {"v_width_range":0.5, "h_width_range":1, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"chest", "color":"purple"},
    ]
    room_info = main(room_edges=edges, random_furniture=furniture_dic, save_path=None, num=100, windows=None, doors=None)
    print(room_info)
    room_info.to_excel(f"""{os.getcwd()}/dataset/room_info.xlsx""", index=False)
    #total.to_pickle(f"""{os.getcwd()}/dataset/room_info.pkl""", index=False)

        