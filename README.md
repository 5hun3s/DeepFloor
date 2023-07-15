# DeepFloor
AIにより家具配置を自動化しよープロジェクト

## インストール
1. pyenvというpythonのバージョン管理を行えるパッケージをインストール（OSなどによってもやり方違う。chatGPTに聞いて下さい） 

2. datasetディレクトリをさくせいし、その中にinspected,uninspectedディレクトリを作成

3. venvファイルがあるでディレクトリで　
`. venv/bin/activate`
を実行
4. その後、そのディレクトリで
`pip install -r requirements.txt`
を実行し必要なライブラリを一括でインストール

## 使用方法
- dataset.py
 ランダムに家具配置の画像と家具の配置データを出力するプログラム。
- GUIlabeling.py
 生成したランダムな家具配置の評価をGUIにより行うためのプログラム