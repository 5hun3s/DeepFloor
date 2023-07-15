# DeepFloor
AIにより家具配置を自動化しよープロジェクト

## インストール
1. main branchをクローンして`pipenv install --ignore-pipfile`<br>➤エラーが出たらpipenvをインストール（pythonのバージョン、ライブラリも含めた仮想環境を構築出来るやつ）

2. pythonファイルがあるディレクトリでdatasetフォルダを作成し、その中にinspected,uninspectedフォルダを作成（githubでは空のディレクトリは保存出来ないらしい）

3. venvファイルがあるでディレクトリで　
`pipenv run python 〇〇`でpythonファイルを実行出来る

## 使用方法
1. `pipenv run pytohn dataset.py`でdataset.pyを実行<br>➤dataset/uninspected内に画像ファイルとdatasetに家具の配置情報が入ったexcelファイルが作成される

2. `pipenv run python GUIlabeling.py`でGUIlabeling.pyを実行<br>➤uninspected内にある画像ファイルが順番に表示される（■が家具、近くにある棒が向いている方向）<br>➤good、badをおすと1で作成したexcelファイル内のtargetカラムにgood、badが入力され、画像はuninspectedからinspectedに移動する

##　pythonファイル
- dataset.py
 ランダムに家具配置の画像と家具の配置データを出力するプログラム。
 if __name__=="__main__":以下をいじると部屋の大きさ、部屋に配置する家具の大きさ、名前などをいじる事ができる

- GUIlabeling.py
 生成したランダムな家具配置の評価をGUIにより行うためのプログラム
 