import os
import PySimpleGUI as sg
import pandas as pd
from itertools import cycle 
from openpyxl import Workbook  

curdir = os.getcwd()
# 画像を含むディレクトリのパス
folder = f"""{curdir}/dataset/uninspected"""

# 画像の拡張子
image_extension = ".png"

# フォルダ内の画像のリストを取得
image_list = [img for img in os.listdir(folder) if img.endswith(image_extension)]
image_list.sort()  # アルファベット順にソート、必要に応じてカスタマイズ
images_cycle = cycle(image_list)  # リストをループできるようにする
image = next(images_cycle)  # 最初の画像
first_image = image

# ウィンドウのレイアウト
layout = [[sg.Image(filename=os.path.join(folder, image), key='-IMAGE-')],
          [sg.Button('good!')],
          [sg.Button("bad!")]]

window = sg.Window('GUIlabeling', layout)

while True:
    event, values = window.read()
    count = 0
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'good!':
        old_image = image
        image = next(images_cycle)
        if image == first_image:
            break
        window['-IMAGE-'].update(filename=os.path.join(folder, image))

        if os.path.isfile(f"""{curdir}/dataset/room_info_reform.xlsx"""):
            df = pd.read_excel(f"""{curdir}/dataset/room_info_reform.xlsx""", engine="openpyxl")
        else:  # If file does not exist, create a new DataFrame
            df = pd.DataFrame()
        df.loc[df["room"]==old_image.split(".")[0], "target"] = "good"
        print(df)
        df.to_excel(f"""{curdir}/dataset/room_info_reform.xlsx""", index=False, engine="openpyxl")
        # 移動元のファイルパス
        source_file = os.path.join(folder, old_image)
        # 移動先のディレクトリパス
        destination_dir = f"""{curdir}/dataset/inspected/"""
        # 移動先のファイルパス
        destination_file = os.path.join(destination_dir, os.path.basename(source_file))
        # ファイルを移動する
        os.rename(source_file, destination_file)

    elif event == "bad!":
        old_image = image
        image = next(images_cycle)
        if image == first_image:
            break
        window['-IMAGE-'].update(filename=os.path.join(folder, image))

        if os.path.isfile(f"""{curdir}/dataset/room_info_reform.xlsx"""):
            df = pd.read_excel(f"""{curdir}/dataset/room_info_reform.xlsx""", engine="openpyxl")
        else:  # If file does not exist, create a new DataFrame
            df = pd.DataFrame()
        df.loc[df["room"]==old_image.split(".")[0], "target"] = "bad"
        print(df)
        df.to_excel(f"""{curdir}/dataset/room_info_reform.xlsx""", index=False, engine="openpyxl")
        # 移動元のファイルパス
        source_file = os.path.join(folder, old_image)
        # 移動先のディレクトリパス
        destination_dir = f"""{curdir}/dataset/inspected/"""
        # 移動先のファイルパス
        destination_file = os.path.join(destination_dir, os.path.basename(source_file))
        # ファイルを移動する
        os.rename(source_file, destination_file)
window.close()