import os
import PySimpleGUI as sg
import pandas as pd
from itertools import cycle 
from openpyxl import Workbook  

curdir = os.getcwd()
# 画像を含むディレクトリのパス
folder = f"""{curdir}/dataset"""
# 保存するエクセルシートの名前
excel_name = "excel_file_name.xlsx"
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
        image = next(images_cycle)
        if image == first_image:
            break
        window['-IMAGE-'].update(filename=os.path.join(folder, image))

        if os.path.isfile(f"""{curdir}/dataset/labeling.xlsx"""):
            df = pd.read_excel(f"""{curdir}/dataset/labeling.xlsx""", engine="openpyxl")
        else:  # If file does not exist, create a new DataFrame
            df = pd.DataFrame()

        data = {'Image Name': [image], 'Status': ['good']} 
        data = pd.DataFrame(data=data, index=[0])
        df = pd.concat([df ,data], ignore_index=True)
        print(df)
        df.to_excel(f"""{curdir}/dataset/labeling.xlsx""", index=False, engine="openpyxl")
        count += 1
    elif event == "bad!":
        image = next(images_cycle)
        if image == first_image:
            break
        window['-IMAGE-'].update(filename=os.path.join(folder, image))

        if os.path.isfile(f"""{curdir}/dataset/labeling.xlsx"""):
            df = pd.read_excel(f"""{curdir}/dataset/labeling.xlsx""", engine="openpyxl")
        else:  # If file does not exist, create a new DataFrame
            df = pd.DataFrame()

        data = {'Image Name': [image], 'Status': ['bad']} 
        data = pd.DataFrame(data=data, index=[0])
        df = pd.concat([df ,data], ignore_index=True)
        print(df)
        df.to_excel(f"""{curdir}/dataset/labeling.xlsx""", index=False, engine="openpyxl")
        count += 1
window.close()