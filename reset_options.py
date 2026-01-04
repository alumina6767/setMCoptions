# 起動構成の設定をチェックする

import tkinter.filedialog
import json
from os import path
import sys

# 起動構成のフォルダ
GAME_DIR = ".minecraft"
if not path.exists(GAME_DIR):
    GAME_DIR = "minecraft"
    if not path.exists(GAME_DIR):
        print("起動構成のフォルダを見つけません。.minecraftやminecraftフォルダと同じ階層に配置してください")
        input()
        sys.exit()


def remove_options_without_key_bind(d):
    """ キーバインド以外の設定を丸ごと消す """
    
    # version はないとバグる
    return {k: v for k, v in d.items() if k.startswith("key_") or k.startswith("version")}


def remove_options(d):
    """ 設定を丸ごと消す """
    
    # version はないとバグる
    return {k: v for k, v in d.items() if k.startswith("version")}


def load_options_from_txt(file_path):
    """ txtから設定の読み込み """
    
    with open(file_path, "r", encoding="utf-8") as f:
        s = f.read().strip()

    d = {_.split(":")[0]: "".join(_.split(":", 1)[1]) for _ in s.split("\n")}

    return d


def check_exists(file_path):
    """ ファイルが存在するかチェックし、なければ作成する """

    if not path.exists(file_path):
        print(f"{file_path} は存在しません")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
        print(f"{file_path} を作成しました")


def load_options_from_properties(file_path):
    """ propertiesから設定の読み込み """

    with open(file_path, "r", encoding="utf-8") as f:
        s = f.read().strip()

    d = {_.split("=")[0]: _.split("=", 1)[1]
         for _ in s.split("\n") if "=" in _}

    return d


def update_options_txt(file_path, file_reset):
    """ マイクラの設定ファイルを更新する """

    # 現在の設定の読み込み
    cur_options = load_options_from_txt(file_path)

    # キーバインド以外の設定を丸ごと消す

    # 設定の読み込み
    if not file_reset:
        new_options = cur_options

    # 設定をリセット
    else:
        new_options = remove_options(cur_options)
        print(f"{file_path} をリセットしました")

    # 撮影に必要な設定項目を追加する
    for o in setting["options"]:
        v = o["option"]["value"]

        # boolの場合は文字列に変換
        if type(v) is bool:
            v = str(v).lower()

        # listの場合は文字列に変換
        elif type(v) is list:
            v = "[" + ",".join([f"\"{_}\"" for _ in v]) + "]"

        # 設定を追加
        new_options[o["option"]["key"]] = v

    # 設定を保存する
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join([f"{k}:{v}" for k, v in new_options.items()]))


def update_json_file(file_path, file_reset):
    """ JSONの設定ファイルを更新する """

    # 現在の設定の読み込み
    if not file_reset:
        with open(file_path, "r", encoding="utf-8") as f:
            try: 
                new_options = json.load(f)
            except json.JSONDecodeError:
                new_options = {}
                print(f"{file_path} の読み込みに失敗しました ファイルをリセットします")

    # 設定をリセット
    else:
        new_options = {}
        print(f"{file_path} をリセットしました")

    # 設定の更新
    for o in setting["options"]:
        new_options = {**new_options, **o["option"]}

    # 設定を保存する
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(new_options, f, indent=2)


def update_properties_file(file_path, file_reset):
    """ propertiesの設定ファイルを更新する """
    
    # 現在の設定の読み込み
    if not file_reset:
        new_options = load_options_from_properties(file_path)
    
    # 設定をリセット
    else:
        new_options = {}
        print(f"{file_path} をリセットしました")

    # 設定の更新
    for o in setting["options"]:
        k = o["option"]["key"]
        v = o["option"]["value"]
        new_options[k] = v if type(v) is not bool else str(v).lower()

    # 設定を保存する
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join([f"{k}={v}" for k, v in new_options.items()]))


# 設定対象を読み込む
print("読み込む設定ファイルを指定してください")

if getattr(sys, 'frozen', False):
    application_path = path.dirname(sys.executable)
elif __file__:
    application_path = path.dirname(__file__)

SETTINGS = None
SETTINGS = tkinter.filedialog.askopenfilename(
    typevariable="json", initialdir=path.abspath(application_path))

if SETTINGS == "":
    print("ファイルが指定されませんでした")
    input()
    sys.exit()

print(f"読み込む設定ファイル: {SETTINGS}")

with open(SETTINGS, "r", encoding="utf-8") as f:
    settings = json.load(f)

# 既にリセットされたファイルを保存
already_reset_files = []

# 設定グループごとに実行
for setting in settings["settings"]:

    file_name = setting["check_file"]
    file_path = path.join(GAME_DIR, file_name)

    # ファイルの存在チェック
    check_exists(file_path)

    # リセット済みかどうか
    file_reset = True if file_path in already_reset_files else False

    # minecraftのTXTファイルの時
    if file_name == "options.txt":
        update_options_txt(file_path, file_reset)

    # JSONファイルの時
    elif file_path.endswith("json"):
        update_json_file(file_path, file_reset)

    # propertiesファイルの時
    elif file_path.endswith("properties"):
        update_properties_file(file_path, file_reset)

    print(f"{file_path} を {setting['name']} に基づいて更新しました")
    
    # リセット済みファイルを保存
    if file_reset:
        already_reset_files.append(file_path)

print("全ての設定を更新しました")
input()
