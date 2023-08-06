import os
import PySimpleGUI as sg
import pandas as pd
from itertools import cycle 
from openpyxl import Workbook  

curdir = os.getcwd()
# 画像を含むディレクトリのパス
folder = f"""{curdir}/dataset/uninspected"""
df = pd.read_csv(f'{curdir}/dataset/room_info_reform.csv')
highscore_name = [name + '.png' for name in df['room_num'].to_list()]
# 画像の拡張子
#image_extension = ".png"

# フォルダ内の画像のリストを取得
#image_list = [img for img in os.listdir(folder) if img.endswith(image_extension)]
all_images = os.listdir(folder)
image_list = [img for img in all_images if img in highscore_name]
image_list.sort()  # アルファベット順にソート、必要に応じてカスタマイズ
images_cycle = cycle(image_list)  # リストをループできるようにする
image = next(images_cycle)  # 最初の画像
first_image = image

# ウィンドウのレイアウト
layout = [[sg.Image(filename=os.path.join(folder, image), key='-IMAGE-')],
          [sg.Text('Please give a score between 0 and 100')],
          [sg.Input(key='-INPUT-')],
          [sg.Button("OK!")]]

window = sg.Window('GUIlabeling', layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'OK!':
        old_image = image
        image = next(images_cycle)
        if image == first_image:
            break
        window['-IMAGE-'].update(filename=os.path.join(folder, image))

        if os.path.isfile(f"""{curdir}/dataset/room_info_reform.csv"""):
            df = pd.read_csv(f"""{curdir}/dataset/room_info_reform.csv""")
        else:  # If file does not exist, create a new DataFrame
            df = pd.DataFrame()
        df.loc[df["room_num"]==old_image.split(".")[0], "target"] = int(values['-INPUT-'])
        #print(df)
        df.to_csv(f"""{curdir}/dataset/room_info_reform.csv""", index=False)
        # 移動元のファイルパス
        source_file = os.path.join(folder, old_image)
        # 移動先のディレクトリパス
        destination_dir = f"""{curdir}/dataset/inspected/"""
        # 移動先のファイルパス
        destination_file = os.path.join(destination_dir, os.path.basename(source_file))
        # ファイルを移動する
        os.rename(source_file, destination_file)
        window["-INPUT-"].update("")#入力された文字を削除

window.close()