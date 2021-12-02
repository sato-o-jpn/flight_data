import streamlit as st
import pandas as pd
import math
import base64

st.title("フライトデータ修正案件用アプリ")

# 何も操作をしていない状態（ファイルアップロードボタンが表示される）
uploaded_file = st.file_uploader("フライトデータ.txtファイルをアップロード", type={"csv", "txt"})
if uploaded_file is not None:
    uploaded_df = pd.read_csv(uploaded_file)

# ファイルをアップロードすると下記のコードが動き出す
if uploaded_file:
    # アップロードしたCSV
    dat = uploaded_df

    # アップロードしたtxtファイルを表示
    st.write("アップロードしたtxtファイル")
    dat

    # データ数
    count = len(dat["time"])

    # 局所迎角（エルロン左）

    La = 10.9
    delta_w = 0
    alpha = dat["alpha"]
    angularSpdX = dat["angularSpdX"]
    tas = dat["TAS"]

    alpha_al = []
    for i in range(len(tas)):
        temp_1 = alpha[i] + delta_w - angularSpdX[i] / math.pi * 180 * La / (tas[i] * 0.5144)
        alpha_al.append(temp_1)

    dat["alpha_al"] = alpha_al

    # 局所迎角（エルロン右）

    alpha_ar = []
    for i in range(len(tas)):
        temp_2 = alpha[i] + delta_w + angularSpdX[i] / math.pi * 180 * La / (tas[i] * 0.5144)
        alpha_ar.append(temp_2)

    dat["alpha_ar"] = alpha_ar

    # 局所迎角（エレベータ）

    delta_h = 0
    Le = 16.3
    elvtrim = dat["elvTrim"]
    angularSpdY = dat["angularSpdY"]

    alpha_e = []
    for i in range(len(tas)):
        temp_3 = alpha[i] * (1 - 0.3) + delta_h - elvtrim[i] - angularSpdY[i] / math.pi * 180 * Le / (tas[i] * 0.5144)
        alpha_e.append(temp_3)

    dat["alpha_e"] = alpha_e

    # 局所迎角（ラダー）

    Lr = 15.8
    beta = dat["beta"]
    angularSpdZ = dat["angularSpdZ"]

    beta_r = []
    for i in range(len(tas)):
        temp_4 = beta[i] - angularSpdZ[i] / math.pi * 180 * Lr / (tas[i] * 0.5144)
        beta_r.append(temp_4)

    dat["beta_r"] = beta_r

    # 音速

    airTemp = dat["airTemp"]

    Va = []
    for i in range(len(tas)):
        temp_5 = 20.0468 * math.sqrt(airTemp[i] + 273.15)
        Va.append(temp_5)

    dat["Va"] = Va

    # ノットをm/sに変換

    VTAS = []
    for i in range(len(tas)):
        temp_6 = tas[i] * 0.5144
        VTAS.append(temp_6)

    dat["VTAS"] = VTAS

    # マッハ数

    M = []
    for i in range(len(tas)):
        temp_7 = VTAS[i] / Va[i]
        M.append(temp_7)

    dat["M"] = M

    # マッハ数補正係数

    Mach = []
    for i in range(len(tas)):
        if M[i] < 0.8:
            temp_8 = 1 / math.sqrt(1 - M[i]**2)
            Mach.append(temp_8)
        else:
            temp_8 = 1 / math.sqrt(1 - 0.8**2)
            Mach.append(temp_8)

    dat["Mach"] = Mach

    # ヒンジモーメント係数（エルロン左）

    b1 = -0.0042
    b2 = -0.0094
    aileronLeft = dat["aileronLeft"]

    Chal = []
    for i in range(len(tas)):
        temp_9 = (b1 * alpha_al[i] + b2 * aileronLeft[i]) * Mach[i]
        Chal.append(temp_9)

    dat["Chal"] = Chal

    # ヒンジモーメント係数（エルロン左）

    b1 = -0.0042
    b2 = -0.0094
    aileronRight = dat["aileronRight"]

    Char = []
    for i in range(len(tas)):
        temp_10 = (b1 * alpha_ar[i] + b2 * aileronRight[i]) * Mach[i]
        Char.append(temp_10)

    dat["Char"] = Char

    # ヒンジモーメント係数（エレベータ左）

    b3 = -0.0042
    b4 = -0.0091
    elevator = dat["elevator"]

    Chel = []
    for i in range(len(tas)):
        temp_11 = (b3 * alpha_e[i] + b4 * elevator[i]) * Mach[i]
        Chel.append(temp_11)

    dat["Chel"] = Chel

    # ヒンジモーメント係数（エレベータ右）

    b3 = -0.0042
    b4 = -0.0091
    elevator = dat["elevator"]

    Cher = []
    for i in range(len(tas)):
        temp_12 = (b3 * alpha_e[i] + b4 * elevator[i]) * Mach[i]
        Cher.append(temp_12)

    dat["Cher"] = Cher

    # ヒンジモーメント係数（ラダー）

    b5 = -0.0027
    b6 = -0.0084
    rudder = dat["rudder"]

    Chr = []
    for i in range(len(tas)):
        temp_13 = (b5 * beta_r[i] + b6 * rudder[i]) * Mach[i]
        Chr.append(temp_13)   

    dat["Chr"] = Chr

    # 動圧

    airDensity = dat["airDensity"]

    Dynamic_p = []
    for i in range(len(tas)):
        temp_14 = (1/2) * airDensity[i] * VTAS[i]**2
        Dynamic_p.append(temp_14)

    dat["Dynamic_p"] = Dynamic_p

    # ヒンジモーメント（エルロン左）

    # 面積(m**2)
    S = 1.6
    # コード長(m)
    c = 0.6

    HMal = []
    for i in range(len(tas)):
        temp_15 = Chal[i] * Dynamic_p[i] * S * c
        HMal.append(temp_15)

    dat["HMal"] = HMal 

    # ヒンジモーメント（エルロン右）

    HMar = []
    for i in range(len(tas)):
        temp_16 = Char[i] * Dynamic_p[i] * S * c
        HMar.append(temp_16)

    dat["HMar"] = HMar

    # ヒンジモーメント（エレベータ左）

    # 面積(m**2)
    S = 3.6
    # コード長(m)
    c = 0.8

    HMel = []
    for i in range(len(tas)):
        temp_17 = Chel[i] * Dynamic_p[i] * S * c
        HMel.append(temp_17)

    dat["HMel"] = HMel

    # ヒンジモーメント（エレベータ右）

    HMer = []
    for i in range(len(tas)):
        temp_18 = Cher[i] * Dynamic_p[i] * S * c
        HMer.append(temp_18)

    dat["HMer"] = HMer

    # ヒンジモーメント（ラダー）

    # 面積(m**2)
    S = 6.4
    # コード長(m)
    c = 1.2

    Hmr = []
    for i in range(len(tas)):
        temp_19 = Chr[i] * Dynamic_p[i] * S * c
        Hmr.append(temp_19)

    dat["Hmr"] = Hmr

    # データの編集
    df_csv = dat.loc[:,["time", "alpha_al", "alpha_ar", "alpha_e", "beta_r", "Va", "VTAS", "M", "Mach", "Chal", "Char", "Chel", "Cher", "Chr", "Dynamic_p", "HMal", "HMar", "HMel", "HMer", "Hmr"]]

    # 完成したルックアップテーブルを表示
    st.write("修正したcsvファイルを表示")
    st.dataframe(df_csv, width=1000, height=300)

    # 完成したCSVファイルのダウンロードリンク
    csv = df_csv.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="flight_data.csv">download</a>'
    st.markdown(f"ダウンロードする {href}", unsafe_allow_html=True)