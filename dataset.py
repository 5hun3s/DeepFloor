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
import copy

def create_rectangle(center, width, height, angle, color):
    """四角形を作成する関数
    Returns
    -------
    rectangle : matplotlib.patches.Rectangle
        描画するための四角形のオブジェクト
    rectangle_polygon : shapely.geometry.polygon.Polygon
        あたり判定を計算するために仮想的に作成された四角形
    """
    rectangle = patches.Rectangle((center[0], center[1]), width, height, angle=angle, fill=False, edgecolor=color)
    rectangle_coordinates = [(center[0], center[1]), 
                             (center[0], center[1] + height), 
                             (center[0] + width, center[1] + height), 
                             (center[0] + width, center[1])]
    rectangle_polygon = Polygon(rectangle_coordinates)
    rectangle_polygon = rotate(rectangle_polygon, angle, origin=(center[0], center[1]))
    return rectangle, rectangle_polygon


def create_line(start, end, color):
    """部屋の枠を表す線を作成する関数
    Returns
    -------
    line : matplotlib.lines.Line2D
        描画するための四角形のオブジェクト
    line_polygon : shapely.geometry.LineString
        あたり判定を計算するために仮想的に作成された四角形
    """
    line_polygon = LineString([(start[0], start[1]), (end[0], end[1])])
    line = Line2D([start[0], end[0]], [start[1], end[1]], color=color)
    return line, line_polygon

def trigonometric_addition_sin(sin_a:float, cos_a:float, b:int):
    """sin(a + b) = sin(a)cos(b) + cos(a)sin(b)を計算します
    """
    return sin_a * math.cos(math.radians(b)) + cos_a * math.sin(math.radians(b))

def trigonometric_addition_cos(sin_a:float, cos_a:float, b:int):
    """cos(a + b) = cos(a)cos(b) - sin(a)sin(b)を計算します"""
    return cos_a * math.cos(math.radians(b)) - sin_a * math.sin(math.radians(b))

def create_direction_line(center, angle, color, furniture_h_len, furniture_v_len):
    """家具の回転を表す棒を描画するための関数
    """
    r = math.sqrt((furniture_h_len/2)**2 + (furniture_v_len/2)**2)

    start_point = (
        center[0] + r * trigonometric_addition_cos((furniture_v_len/2)/r, (furniture_h_len/2)/r, angle),
        center[1] + r * trigonometric_addition_sin((furniture_v_len/2)/r, (furniture_h_len/2)/r, angle)
        )
    end_point = (
        center[0] + math.cos(math.radians(angle)) + r * trigonometric_addition_cos((furniture_v_len/2)/r, (furniture_h_len/2)/r, angle), 
        center[1] + math.sin(math.radians(angle)) + r * trigonometric_addition_sin((furniture_v_len/2)/r, (furniture_h_len/2)/r, angle)
        )
    line, line_polygon = create_line(start_point, end_point, color)
    return line, line_polygon

def plot_line(line, ax):
    ax.add_line(line)
    
def find_center(points):
    """中心を見つけるための関数
    """
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    center_x = sum(x_coords) / len(points)
    center_y = sum(y_coords) / len(points)
    return (center_x, center_y)


def calculate_angle(point, center):
    """角度を計算する関数
    """
    return math.atan2(point[1] - center[1], point[0] - center[0])

def sort_points(points):
    """各点を角度に基づいてソートする関数
    """
    center = find_center(points)
    return sorted(points, key=lambda point: calculate_angle(point, center))

def multi_check_overlap(obj1, objs2:list):
    """あたり判定を計算する関数
    
    Parameters
    ---------
    obj1 : shapely.geometry.polygon.Polygon
        あたり判定を計算するために作成された四角形のオブジェクト
    obj2 : list
        あたり判定を計算するために作成された四角形のオブジェクトが複数格納されたリスト
    """
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

        Returns
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
            draw_direction, _ = create_direction_line(coord, furniture.rotation, furniture.color, furniture.h_width, furniture.v_width) # add this line
            plot_line(draw_direction, ax)#add this line
            self.direction_lines.append(draw_direction)
            if (multi_check_overlap(calculate_furniture, self.line_objects)) or (coord[0]<min_x) or (coord[0]>max_x) or (coord[1]<min_y) or (coord[1]>max_y):
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
        """家具を部屋、他の家具とかさならないように配置するメソッド

        Parameters
        ---------
        random_furniture : list
            ランダムに配置する家具の情報が辞書オブジェクトで入ったリスト
        
        Returns
        -------
        furniture_info : list
            各家具の情報が記録してある辞書オブジェクトが入ってるリスト
        """
        x_coords = [edge[0] for edge in self.edges]
        y_coords = [edge[1] for edge in self.edges]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        furniture_info = list()
        for f_dic in random_furniture:
            dic = dict()
            while True:
                """家具の幅もランダム
                #dic["v_width"] = random.randint(f_dic["v_width_range"][0], f_dic["v_width_range"][1])
                #dic["h_width"] = random.randint(f_dic["h_width_range"][0], f_dic["h_width_range"][1])
                #dic["rotation"] = random.choice(f_dic["rotation_range"])
                #dic["name"] = f_dic["name"]
                #dic["color"] = f_dic["color"]
                """
                """置く場所と角度だけランダム
                dic["v_width"] = f_dic["v_width_range"]
                dic["h_width"] = f_dic["h_width_range"]
                dic["rotation"] = random.choice(f_dic["rotation_range"])
                dic["name"] = f_dic["name"]
                dic["color"] = f_dic["color"]
                """
                #dic["coord"] = [[random.randint(min_x, max_x), random.randint(min_y, max_y)]]
                dic["name"] = f_dic["name"]
                delta = 0.1
                """
                if ("restriction" in f_dic) and (f_dic["restriction"] == "alongwall direct center"):
                    
                    rand = random.choice([0, 1, 2, 3])
                    print(rand)
                    if rand == 0:
                        dic["x"], dic["y"] = min_x + f_dic["v_width_range"] + delta, random.randint(min_y, max_y)
                        dic["rotation"] = random.choice(f_dic["rotation_range"])
                    elif rand == 1:
                        dic["x"], dic["y"] = random.randint(min_x, max_x), max_y - f_dic["v_width_range"] - delta
                        dic["rotation"] = random.choice(f_dic["rotation_range"])
                    elif rand == 2:
                        dic["x"], dic["y"] = max_x - f_dic["v_width_range"] - delta, random.randint(min_y, max_y)
                        dic["rotation"] = 90
                    elif rand == 3:
                        dic["x"], dic["y"] = random.randint(min_x, max_x), min_y + f_dic["v_width_range"] + delta
                        dic["rotation"] = random.choice(f_dic["rotation_range"])
                """
                if ("restriction" in f_dic) and (f_dic["restriction"] == "alongwall"):
                    rand = random.choice([0, 1])
                    if rand == 0:
                        dic["x"], dic["y"] = random.choice([min_x + delta, max_x - delta]), random.randint(min_y, max_y)
                    elif rand == 1:
                        dic["x"], dic["y"] = random.randint(min_x, max_x), random.choice([min_y + delta, max_y - delta])
                    dic["rotation"] = random.choice(f_dic["rotation_range"])
                elif "restriction" not in f_dic:
                    dic["x"], dic["y"] = random.randint(min_x, max_x), random.randint(min_y, max_y)
                    dic["rotation"] = dic["rotation"] = random.choice(f_dic["rotation_range"])

                #elif ("restriction" in f_dic) and (f_dic["restriction"] == "alongwall")
                fur = Furniture(f_dic["v_width_range"], f_dic["h_width_range"], dic["rotation"], f_dic["name"], f_dic["color"])
                error_flag = self.plot_furniture(ax, [fur], [[dic["x"], dic["y"]]])#ポジションのエラーを追加
                #error_flag = self.plot_furniture(ax, [furniture], dic["coord"])
                if (error_flag[0]!=0):
                    self.clear_furniture(ax, furniture_index=-1)
                elif (error_flag[0]==0):
                    furniture_info.append(dic)
                    break
        return furniture_info
   
def main(room_edges:list, random_furniture:list, num:int, windows:list=None, doors:list=None, random_produce_n:int=3):
    """データセットの作成にメインで使う関数

    Parameters
    ---------
    room_edges : list
        部屋の隅の座標をいれたリスト（正方形、長方形なら４つ）
    random_furniture : list
        配置する家具の情報を辞書オブジェクトでいれたリスト
    num : int
        何パターンの家具配置画像を出力するか
    windows : list
        部屋の窓の端を示したもの(詳しくはRoomクラスの説明で)
    doors : list
        部屋のドアの端を示したもの(詳しくはRoomクラスの説明で)
    random_produce_n : int
        引数で渡された家具を複製して配置する家具の最大値

    Returns
    -------
    room_info : pd.DataFrame
        各家具配置パターンでの家具の情報が入ったdataframe
    """
    if os.path.isfile(f"""{os.getcwd()}/dataset/room_info.xlsx"""):
        room_info = pd.read_excel(f"""{os.getcwd()}/dataset/room_info.xlsx""", engine="openpyxl")
    else:
        room_info = pd.DataFrame()
    image_num = len(os.listdir(f"""{os.getcwd()}/dataset/uninspected""")) + len(os.listdir(f"""{os.getcwd()}/dataset/inspected"""))# 現在生成されたデータ数をカウント
    room_h_len, room_v_len = find_max_values(room_edges)# 部屋の縦幅、横幅を取得
    room_h_len -= 1
    room_v_len -= 1
    for _ in range(num):
        fig, ax = plt.subplots()
        room = Room(room_edges, windows=windows, doors=doors)
        room.plot_room(ax)
        #家具をランダムで複製
        new_random_furniture = make_random_furniture_set(random_furniture, random_produce_n)
        furniture_info_list = room.random_plot_furniture(random_furniture=new_random_furniture, ax=ax)
       
        #各家具の相対的な距離を算出したカラムを追加
        furniture_name_non_duplicated = ["sofa", "desk", "chair", "TV", "light", "plant", "shelf", "chest", "bed"]
        furniture_names = [f"{item}_{i}" for item in furniture_name_non_duplicated for i in range(1, 4)]#[sofa_1, sofa_2, ..]
        for i in furniture_info_list:
            for furniture_name in furniture_names:
                if i["name"]!=furniture_name:
                    distance = find_dict_by_name(furniture_info_list, furniture_name, i)
                    i[f"""d_{furniture_name}"""] = distance
        
        for furniture_info in furniture_info_list:
            df = pd.DataFrame(furniture_info, index=[0])
            df["room"] = f"""room_{str(_ + image_num)}"""# dataframeに生成されたランダムな部屋配置の番号を追加
            
            #部屋の縦横二関してのカラムを追加
            df["room_h_length"] = room_h_len
            df["room_v_length"] = room_v_len
            
            room_info = pd.concat([room_info, df])
        fig.savefig(f"""{os.getcwd()}/dataset/uninspected/room_{str(_ + image_num + 1)}.png""")
    room_info["target"] = "uninspected"
    return room_info

def find_max_values(arr):
    max_val_1 = max(arr, key=lambda x: x[0])[0]
    max_val_2 = max(arr, key=lambda x: x[1])[1]
    return max_val_1, max_val_2
   
def calculate_distance(p1, p2):
    return math.sqrt((p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2)

def find_dict_by_name(dict_list, name, selfdict):
    """家具同士の距離を算出したカラムを作成する際に使用した関数

    Parameters
    ---------
    dict_list : list
        他の家具の情報が辞書形式で入ったリスト
        ex) [{"name":"bed_1", "x":4, "y":3}, {"name":"sofa_1", "x":8, "y":2}]
    name : str
        selfdictの家具との距離を測りたい家具の名前
        ex) bed_1
    selfdict : dict
        主観的な家具
        ex) {"name":"sofa_1", "x":8, "y":2}
    
    Returns
    ------
    distance : float
        二つの家具の距離
        ex) sofa_1とbed_1の距離
    """
    selfname = selfdict["name"]
    for dictionary in dict_list:
        if (dictionary.get("name") == name) and (name != selfname):
            distance = calculate_distance(selfdict, dictionary)
            return distance
    return 0

def make_random_furniture_set(random_furniture, random_produce_n):
    """家具の複製を行う関数

    Parameters
    ---------
    random_furniture : list
        配置する家具の情報を辞書オブジェクトでいれたリスト
    random_produce_n : int
        引数で渡された家具を複製して配置する家具の最大値

    Returns
    ------
    dic_list : list
        ランダムに複製された家具の情報が詰め込まれた辞書オブジェクトが複数入ったリスト
    """
    dic_list = list()
    for f in random_furniture:
        produce_n = random.randint(0, random_produce_n)#家具をおかない場合も発生
        if produce_n != 0:
            for n in range(produce_n):
                cur_dic = copy.deepcopy(f)
                cur_dic["name"] = f"""{f["name"]}_{n+1}"""
                dic_list.append(cur_dic)
        elif produce_n == 0:
            continue
    return dic_list
        
if __name__ ==  "__main__":
    room_h_length = 10
    room_v_length = 10
    edges = [
        [1, 1],
        [1, room_v_length + 1],
        [room_h_length + 1, room_v_length + 1],
        [room_h_length + 1, 1]
    ]

    winds = [
        {"start":[1,5], "end":[1,6]},
        {"start":[5,10], "end":[6,10]},
    ]
    dors = [
        {"start":[10, 5], "end":[10, 6]}
    ]
    """restrictionは家具の配置制限
    alongwall : 壁際に配置する
    """
    furniture_dic = [
        {"v_width_range":0.5, "h_width_range":1.4, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"sofa", "color":"brown"},
        {"v_width_range":0.6, "h_width_range":1.2, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"desk", "color":"orange"},
        {"v_width_range":0.5, "h_width_range":0.5, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"chair", "color":"red"},
        #{"v_width_range":0.05, "h_width_range":1.2, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"TV", "color":"blue"},
        {"v_width_range":0.4, "h_width_range":1.8, "rotation_range":[0, 90, 180, 270, 360], "name":"TV stand", "color":"navy", "restriction":"alongwall"},
        {"v_width_range":0.2, "h_width_range":0.2, "rotation_range":[0, 90, 180, 270, 360], "name":"light", "color":"gold", "restriction":"alongwall"},
        {"v_width_range":0.2, "h_width_range":0.2, "rotation_range":[0, 90, 180, 270, 360], "name":"plant", "color":"green", "restriction":"alongwall"},
        {"v_width_range":0.3, "h_width_range":0.4, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"shelf", "color":"magenta"},
        {"v_width_range":0.5, "h_width_range":1, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"chest", "color":"purple"},
    ]
    room_info = main(room_edges=edges, random_furniture=furniture_dic, num=20, windows=None, doors=None)
    print(room_info)
    print(room_info.shape)
    room_info.to_excel(f"""{os.getcwd()}/dataset/room_info.xlsx""", index=False)
    #total.to_pickle(f"""{os.getcwd()}/dataset/room_info.pkl""", index=False)

        