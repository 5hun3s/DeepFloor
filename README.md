# DeepFloor
AIにより家具配置を自動化しよープロジェクト

## インストール
1. pythonのインストール<br>
pythonがインストールされていないならインストールする<br>
https://www.python.org/downloads/

2. pipenvのインストール<br>
ターミナル上で<br>
`pip install pipenv`<br>
を実行しpipenvのインストール

3. pyenvのインストール<br>
macOSで操作する場合は<br>
`brew install pyenv`<br>
を実行しpyenvをインストール

4. 仮想環境の再現<br>
Pipfile、Pipfile.lockがあるディレクトリで<br>
`pipenv install --ignore-pipfile`<br>
を実行し仮想環境を再現

5. フォルダの作成<br>
そのままディレクトリでdatasetフォルダを作成して、その中にinspected,uninspectedフォルダも作成<br>
（githubでは空のディレクトリは保存出来ないらしい）

6. pythonファイルの実行<br>
そのままのディレクトリで<br>
```
pipenv run python dataset.py
pipenv run python GUIlabeling.py
```
を順番に実行

## 使用方法
1. `pipenv run pytohn dataset.py`でdataset.pyを実行<br>➤dataset/uninspected内に画像ファイルとdatasetに家具の配置情報が入ったcsvファイルが作成される

2. `pipenv run python GUIlabeling.py`でGUIlabeling.pyを実行<br>➤uninspected内にある画像ファイルが順番に表示される（■が家具、棒が向いている方向を表している）<br>➤OKをおすと1で作成したexcelファイル内のtargetカラムに点数が入力され、画像はuninspectedからinspectedに移動する

## pythonファイル
- dataset.py
 ランダムな家具配置の画像と家具の配置データcsvに出力するプログラム。
 if __name__=="__main__":以下をいじると部屋の大きさ、部屋に配置する家具の大きさ、名前などをいじる事ができる

- GUIlabeling.py
 dataset.pyで生成したランダムな家具配置の評価を行うための関数
 