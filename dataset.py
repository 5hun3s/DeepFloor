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
import re
from restriction import set_alongwall_dir_ctr, set_alongwall, set_combo, set_facing

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

def trigonometric_addition_sin_minus(sin_a:float, cos_a:float, b:int):
    """sin(a - b) = sin(a)cos(b) - cos(a)sin(b)を計算します
    """
    return sin_a * math.cos(math.radians(b)) - cos_a * math.sin(math.radians(b))

def trigonometric_addition_cos(sin_a:float, cos_a:float, b:int):
    """cos(a + b) = cos(a)cos(b) - sin(a)sin(b)を計算します"""
    return cos_a * math.cos(math.radians(b)) - sin_a * math.sin(math.radians(b))

def trigonometric_addition_cos_minus(sin_a:float, cos_a:float, b:int):
    """cos(a - b) = cos(a)cos(b) + sin(a)sin(b)を計算します"""
    return cos_a * math.cos(math.radians(b)) + sin_a * math.sin(math.radians(b))

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
class RedoLoop(Exception): pass

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
            if (multi_check_overlap(calculate_furniture, self.line_objects)) or (coord[0]<=min_x) or (coord[0]>=max_x) or (coord[1]<=min_y) or (coord[1]>=max_y):
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
        print(random_furniture)
        x_coords = [edge[0] for edge in self.edges]
        y_coords = [edge[1] for edge in self.edges]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        max_attempts = 50
        for _ in range(max_attempts):
            restart = False  # ループを再開するかどうかをチェックするフラグ
            furniture_info = list()
            for f_dic in random_furniture:
                #print("second")
                dic = dict()
                prob = f_dic['prob']
                name = f_dic['name']
                if random.random() < prob:
                    #print("third")
                    counter = 0
                    while True:
                        dic["name"] = name
                        dic['exist'] = 1
                        dic["v_width"] = f_dic["v_width_range"]#家具の長さ追加した
                        dic["h_width"] = f_dic["h_width_range"]
                        if ("restriction" in f_dic) and ("alongwall" in f_dic["restriction"]):
                            dic["x"], dic["y"], dic["rotation"] = set_alongwall(min_x, max_x, min_y, max_y, f_dic["rand_rotation"], delta=0.01)
                        elif ("restriction" in f_dic) and ("alongwall direction center" in f_dic["restriction"]):
                            dic["x"], dic["y"], dic["rotation"] = set_alongwall_dir_ctr(f_dic["v_width_range"], min_x, max_x, min_y, max_y, delta=0.01)
                        elif ("restriction" in f_dic) and ("set" in f_dic["restriction"]):
                            set_furnitures = [item for item in furniture_info if re.match(f_dic["set_furniture"] + "_" + r'\d+', item['name'])]
                            if len(set_furnitures) == 0:#setする家具が配置されていない場合その家具も配置されない
                                dic["x"], dic["y"] = random.uniform(min_x, max_x), random.uniform(min_y, max_y)
                                dic["rotation"] = random.choice(f_dic["rand_rotation"])
                            elif len(set_furnitures) != 0:
                                set_furniture = random.choice(set_furnitures)
                                dic["x"], dic["y"], dic["rotation"] = set_combo(dic["v_width"], dic["h_width"], min_x, max_x, min_y, max_y, set_furniture=set_furniture, delta=0.01)
                        elif ("restriction" in f_dic) and ("facing" in f_dic["restriction"]):
                            face_furnitures = [item for item in furniture_info if re.match(f_dic["face_furniture"] + "_" + r'\d+', item['name'])]
                            if len(face_furnitures) == 0:#setする家具が配置されていない場合その家具も配置されない
                                dic["x"], dic["y"] = random.uniform(min_x, max_x), random.uniform(min_y, max_y)
                                dic["rotation"] = random.choice(f_dic["rand_rotation"])
                            elif len(face_furnitures) != 0:
                                face_furniture = random.choice(face_furnitures)
                                dic["x"], dic["y"], dic["rotation"] = set_facing(dic["v_width"], dic["h_width"], min_x, max_x, min_y, max_y, face_furniture=face_furniture, delta=0.01)
                        elif "restriction" not in f_dic:
                            dic["x"], dic["y"] = random.uniform(min_x, max_x), random.uniform(min_y, max_y)
                            dic["rotation"] = random.choice(f_dic["rand_rotation"])
                        fur = Furniture(dic["v_width"], dic["h_width"], dic["rotation"], dic["name"], f_dic["color"])
                        error_flag = self.plot_furniture(ax, [fur], [[dic["x"], dic["y"]]])#ポジションのエラーを追加
                        #error_flag = self.plot_furniture(ax, [furniture], dic["coord"])
                        if error_flag[0]!=0:
                            self.clear_furniture(ax, furniture_index=-1)
                            counter += 1
                        elif error_flag[0]==0:
                            furniture_info.append(dic)
                            #print("break")
                            break
                        if counter>50:#50回以上エラーが出たら論理的におけないと判断し、もう一度全ての家具を置きなおす
                            self.clear_furniture(ax, all_clear=True)
                            #print("clear")
                            restart = True
                            break
                        #print(counter)
                    if restart:
                        break
                    
                else:
                    dic["name"] = name
                    dic['exist'] = 0
                    dic["x"], dic["y"] = 0, 0
                    dic["rotation"] = 0
                    dic["v_width"] = 0
                    dic["h_width"] = 0
                    furniture_info.append(dic)
            if not restart:  # もし再開フラグがFalseの場合、外部ループを終了
                break
        print("final")
        return furniture_info
   
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

def make_random_furniture_prob_set(random_furniture, max_produce_n:int=3):
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
    prob_dict ={'bed':[0.9, 0, 0],
                'sofa':[0.9, 0, 0],
                'desk':[0.9, 0, 0],
                'chair':[1, 0.2, 0.2],
                'TV stand':[0.8, 0, 0],
                'light':[0.9, 0.1, 0.1],
                'plant':[0.7, 0.1, 0.1],
                'shelf':[0.9, 0.1, 0],
                'chest':[0.9, 0.1, 0]}
    dic_list = list()
    for f in random_furniture:
        produce_n = 3 #家具をおかない場合も発生
        for n in range(produce_n):
            cur_dic = copy.deepcopy(f)
            cur_dic['prob'] = prob_dict[cur_dic['name']][n]
            cur_dic["name"] = f"""{f["name"]}_{n+1}"""            
            dic_list.append(cur_dic)
        continue
    return dic_list

def reformat_dataframe(df):
    # 'room'カラムでグループ化し、その他のカラムを連結します
    df_grouped = df.groupby('room').agg(lambda x: x.tolist())

    # 新しいデータフレームを作成します
    df_new = pd.DataFrame()

    # グループ化したデータフレームをループして、新しいカラムを作成します
    for index, row in df_grouped.iterrows():
        for furniture_name in df.columns:
            if furniture_name != 'room':
                # カラム名を`<furniture_name>_<column>`形式に変更します
                new_columns = [f'{furniture_name}_{i}' for i in range(len(row[furniture_name]))]
                
                # 新しいカラムをデータフレームに追加します
                for i, new_column in enumerate(new_columns):
                    df_new.at[index, new_column] = row[furniture_name][i]

    # 新しいデータフレームを返します
    return df_new

def rereformat_dataframe(df):
    new_df = pd.DataFrame()
    room_num_unique_list = list(df["room"].unique())
    all_column_list = df.columns.tolist()
    remove_column_list = ["room", "room_h_length", "room_v_length", "target", "name"]
    column_list = [x for x in all_column_list if x not in remove_column_list]
    for room_num in room_num_unique_list:
        df_split = df[df["room"] == room_num]
        df_split = df_split.reset_index(drop=True)
        room_h, room_v = df_split.at[0 ,"room_h_length"], df_split.at[0 ,"room_v_length"]
        dic = {"room_num":room_num, "room_v":room_v, "room_h":room_h, "target":"uninspected"}
        for index in range(len(df_split)):
            df_split_one_line = df_split.iloc[index, :]
            name = df_split_one_line["name"]
            for column in column_list:
                dic[f"""{name}_{column}"""] = df_split_one_line[column]
            new_df_split_one_line = pd.DataFrame(dic, index=[0])
        new_df = pd.concat([new_df, new_df_split_one_line], ignore_index=True)
    return new_df
            
                
    

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
    if os.path.isfile(f"""{os.getcwd()}/dataset/room_info.csv"""):
        room_info = pd.read_csv(f"""{os.getcwd()}/dataset/room_info.csv""")
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
        new_random_furniture = make_random_furniture_prob_set(random_furniture, random_produce_n)
        furniture_info_list = room.random_plot_furniture(random_furniture=new_random_furniture, ax=ax)
       
        #各家具の相対的な距離を算出したカラムを追加
        furniture_name_non_duplicated = ["sofa", "desk", "chair", "TV", "light", "plant", "shelf", "chest", "bed"]
        furniture_names = [f"{item}_{i}" for item in furniture_name_non_duplicated for i in range(1, 4)]#[sofa_1, sofa_2, ..]
        for i in furniture_info_list:
            for furniture_name in furniture_names:
                if i['exist'] == 0:
                    i[f'd_{furniture_name}'] = 0
                elif i["name"]!=furniture_name:
                    distance = find_dict_by_name(furniture_info_list, furniture_name, i)
                    i[f"""d_{furniture_name}"""] = distance
                else:
                    i[f'd_{furniture_name}'] = 0
        
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

def main_rand_room_size(min_room_size:list, max_room_size:list, random_furniture:list, num:int, windows:list=None, doors:list=None, random_produce_n:int=3):
    """データセットの作成にメインで使う関数

    Parameters
    ---------
    min_room_size : list
        部屋の最小サイズ
    max_room_size : list
        部屋の最大サイズ
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

    if os.path.isfile(f"""{os.getcwd()}/dataset/room_info.csv"""):
        room_info = pd.read_csv(f"""{os.getcwd()}/dataset/room_info.csv""")
    else:
        room_info = pd.DataFrame()
    image_num = len(os.listdir(f"""{os.getcwd()}/dataset/uninspected""")) + len(os.listdir(f"""{os.getcwd()}/dataset/inspected"""))# 現在生成されたデータ数をカウント
    for _ in range(num):
        fig, ax = plt.subplots()
        room_h_length = random.randint(min_room_size[0], max_room_size[0])
        room_v_length = random.randint(min_room_size[1], max_room_size[1])
        edges = [
            [1, 1],
            [1, room_v_length + 1],
            [room_h_length + 1, room_v_length + 1],
            [room_h_length + 1, 1]
        ]
        room_h_len, room_v_len = find_max_values(edges)# 部屋の縦幅、横幅を取得
        room_h_len -= 1
        room_v_len -= 1
        room = Room(edges, windows=windows, doors=doors)
        room.plot_room(ax)
        #家具をランダムで複製
        new_random_furniture = make_random_furniture_prob_set(random_furniture, random_produce_n)
        furniture_info_list = room.random_plot_furniture(random_furniture=new_random_furniture, ax=ax)
       
        #各家具の相対的な距離を算出したカラムを追加
        furniture_name_non_duplicated = ["sofa", "desk", "chair", "TV", "light", "plant", "shelf", "chest", "bed"]
        furniture_names = [f"{item}_{i}" for item in furniture_name_non_duplicated for i in range(1, 4)]#[sofa_1, sofa_2, ..]
        for i in furniture_info_list:
            for furniture_name in furniture_names:
                if i['exist'] == 0:
                    i[f'd_{furniture_name}'] = 0
                elif i["name"]!=furniture_name:
                    distance = find_dict_by_name(furniture_info_list, furniture_name, i)
                    i[f"""d_{furniture_name}"""] = distance
                else:
                    i[f'd_{furniture_name}'] = 0
        
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


if __name__ ==  "__main__":
    """
    room_h_length = 4
    room_v_length = 6
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
    """



    """restrictionは家具の配置制限
    alongwall : 壁際に配置する
    set : 一緒に配置する家具を指定する
    facing : 家具が向かい合うように配置する
    """
    for __ in range(20):
        furniture_dic = [
            {"v_width_range":1, "h_width_range":1.95, "rand_rotation":[0,90,180,270], "name":"bed", "color":"blue", "restriction":["alongwall"]},
            {"v_width_range":0.6, "h_width_range":1.2, "rand_rotation":[0,90,180,270], "name":"desk", "color":"orange", "restriction":["alongwall"]},
            {"v_width_range":0.5, "h_width_range":0.5, "rand_rotation":[0, 90, 180, 270], "name":"chair", "color":"red", "restriction":["set", "alomgwall"], "set_furniture":"desk"},
            #{"v_width_range":0.05, "h_width_range":1.2, "rotation_range":[0, 45, 90, 135, 180, 225, 270, 315, 360], "name":"TV", "color":"blue"},
            {"v_width_range":1.8, "h_width_range":0.4, "rand_rotation":[0,90,180,270], "name":"TV stand", "color":"navy", "restriction":["alongwall direction center"]},
            {"v_width_range":1.4, "h_width_range":0.5, "rand_rotation":[0, 45, 90, 135, 180, 225, 270, 315], "name":"sofa", "color":"brown", "restriction":["facing"], "face_furniture":"TV stand"},
            {"v_width_range":0.2, "h_width_range":0.2, "rand_rotation":[0,90,180,270], "name":"light", "color":"gold", "restriction":["alongwall"]},
            {"v_width_range":0.2, "h_width_range":0.2, "rand_rotation":[0, 90, 180, 270], "name":"plant", "color":"green", "restriction":["alongwall"]},
            {"v_width_range":0.3, "h_width_range":0.4, "rand_rotation":[0,90,180,270], "name":"shelf", "color":"magenta", "restriction":["alongwall direction center"]},
            {"v_width_range":1, "h_width_range":0.5, "rand_rotation":[0,90,180,270], "name":"chest", "color":"purple", "restriction":["alongwall direction center"]},
        ]
        #room_info = main(room_edges=edges, random_furniture=furniture_dic, num=20, windows=None, doors=None)
        room_info = main_rand_room_size(min_room_size=[3, 3], max_room_size=[6, 6] ,random_furniture=furniture_dic, num=10, windows=None, doors=None)

        #room_info.to_csv(f"""{os.getcwd()}/dataset/room_info.csv""", index=False)  # CSVファイルを読み込みます
        df_reform = rereformat_dataframe(room_info)  # 関数を呼び出してデータフレームを変換します
        curdir = os.getcwd()
        if os.path.isfile(f"""{curdir}/dataset/room_info_reform.csv"""):
            df = pd.read_csv(f"""{curdir}/dataset/room_info_reform.csv""")
            df = pd.concat([df, df_reform])
            df.to_csv(f"""{os.getcwd()}/dataset/room_info_reform.csv""", index=False)
            print(df.shape)
        else:  # If file does not exist, create a new DataFrame
            df_reform.to_csv(f"""{os.getcwd()}/dataset/room_info_reform.csv""", index=False)  # 新しいデータフレームを表示します
            print(df_reform.shape)
        print('finished')
