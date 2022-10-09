""" Library """
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import json
import sprapi as sa
import time
import threading
import sys
import subprocess as sp

""" 特殊動作 """
def win_quit():
    """
    xボタンを押したときの動作
    --------
    ホスト:ホストステータスを0にする
    クライアント:camera_main.pyを終了する

    未解決
    --------
    
    """
    if mode == 0:
        HOST.write_state({"state_code": 0})
    elif mode == 1:
        with open("camera_cmd.txt", "w") as f:
            f.write("q")
    sys.exit()

def host():
    """
    HOSTを作成する
    --------
    google sheetsにHOSTとして接続し、クライアント数を送信する

    未解決
    --------

    元画面
    --------
    Win_Mode()
    
    選択肢
    --------
    サーバー重複エラー:Win_Error()
    成功:Win_Manual()
    """
    global HOST, mode
    try:
        HOST = sa.MVPHost(client_all)
    except RuntimeError:
        flm_Load.destroy()
        Win_Error()
    else:
        flm_Load.destroy()
        Win_Manual()
        mode = 0

def client():
    """
    CLIENTを作成する
    --------
    google sheetsにCLIENTとして接続する

    元画面
    --------
    Win_Mode()

    未解決
    --------

    選択肢
    --------
    なんらかのエラー:Win_Error()
    成功:Win_Manual()
    """
    global CLIENT, mode, team_num
    try:
        CLIENT = sa.MVPClient()
        team_num = CLIENT.client_id
    except:
        flm_Load.destroy()
        Win_Error2()
    else:
        flm_Load.destroy()
        Win_Camera()
        mode = 1

""" 関数呼び出し用スレッド """
def host_start():
    """
    host()の呼び出し
    --------
    google sheetsにHOSTとして接続する

    元画面
    --------
    Win_Mode()

    未解決
    --------

    """
    th = threading.Thread(target=host)
    th.start()

def client_start():
    """
    client()の呼び出し
    --------
    google sheetsにCLIENTとして接続する

    元画面
    --------
    Win_Mode()

    未解決
    --------

    """
    th = threading.Thread(target=client)
    th.start()

def get_cl():
    """
    get_start()の呼び出し
    --------
    クイズ開始を検知する

    元画面
    --------
    Win_Camera()

    未解決
    --------

    """
    th = threading.Thread(target=get_start)
    th.start()

def cam_err():
    """
    sub_get()の呼び出し
    --------
    カメラの正常動作またはエラーを検知する

    元画面
    --------
    Win_Camera()

    未解決
    --------

    """
    th = threading.Thread(target=sub_get)
    th.start()

""" ボタン用関数 """
def mode_host():
    """
    Win_Mode() -> Win_CNum()
    --------
    ほかの動作はありません

    未解決
    --------

    """
    flm_Mode.destroy()
    Win_CNum()

def mode_client():
    """
    Win_Mode() -> Win_Load() -> Win_Error() or Win_Manual()
    --------
    client_start()を呼び出し、CLIENTとしてgoogle sheetsと接続する

    未解決
    --------

    """
    global flm_Load
    flm_Mode.destroy()
    flm_Load = tk.Frame(root)
    flm_Load.pack(expand=1, fill=tk.BOTH)
    lbl_Load = tk.Label(flm_Load, text="Loading...", font=("Arial", 30))
    lbl_Load.place(x=480, y=135, anchor=tk.CENTER)
    client_start()

def mode_make():
    """
    make_quiz.pyを開始 -> mainGUI.pyを削除
    --------
    ほかの動作はありません

    未解決
    --------

    """
    sp.Popen(["python", "make_quiz.py"], shell=True)
    root.destroy()

def error_back():
    """
    Win_Error() -> Win_Mode()
    --------
    ほかの動作はありません

    未解決
    --------

    """
    flm_Error.destroy()
    Win_Mode()

def error_back2():
    """
    Win_Error() -> Win_Mode()
    --------
    ほかの動作はありません

    未解決
    --------

    """
    flm_Error2.destroy()
    Win_Mode()

def count_cl():
    """
    画面遷移なし
    --------
    spn_Numの値(=クライアント数)を取得する

    未解決
    --------

    """
    global client_all
    client_all = spn_Num.get()

def cnum_ok():
    """
    Win_CNum() -> Win_Load() -> Win_Error() or Win_Manual()
    --------
    ほかの動作はありません

    未解決
    --------

    """
    global flm_Load
    count_cl()
    flm_CNum.destroy()
    flm_Load = tk.Frame(root)
    flm_Load.pack(expand=1, fill=tk.BOTH)
    lbl_Load = tk.Label(flm_Load, text="Loading...", font=("Arial", 30))
    lbl_Load.place(x=480, y=135, anchor=tk.CENTER)
    host_start()

def manual_dia():
    global quizpath
    quizpath = filedialog.askopenfilename(filetypes = [('クイズファイル','*.json')] , initialdir = './')

def manual_next():
    global Quiz_List, quizdata
    flm_Manual.destroy()
    print(quizpath)
    print(type(quizpath))
    if quizpath != None and quizpath != "":
        with open(quizpath, "r", encoding="utf-8") as f:
            quizdata = json.load(f)
    Quiz_List = HOST.read_quiz()
    Win_HWait()

def hwait_ok():
    flm_HWait.destroy()
    data = HOST.read_state()
    data["state_code"] = 20
    HOST.write_state(data)
    Win_Quiz()

def camera_next():
    flm_Camera.destroy()
    Win_Step()

def quiz_timer():
    global TIMER, HOST_MSG
    if TIMER == 0:
        TIMER = 5
        HOST_MSG = "正答の表示まで"
        lbl_status["text"] = HOST_MSG
        quiz_camdata()
        return
    TIMER -= 1
    lbl_Timer["text"] = TIMER
    lbl_Timer.after(1000, quiz_timer)

def quiz_camdata():
    global TIMER, HOST_MSG
    if TIMER == 0:
        TIMER = 5
        HOST_MSG = "得点の表示まで"
        lbl_status["text"] = HOST_MSG
        if (Quiz_List[nowquiz-1]["answer"]):
            lbl_QFalse.place_forget()
        else:
            lbl_QTrue.place_forget()
        quiz_trueans()
        return
    TIMER -= 1
    lbl_Timer["text"] = TIMER
    lbl_Timer.after(1000, quiz_camdata)


def quiz_trueans():
    global TIMER, HOST_MSG
    if TIMER == 0:
        TIMER = 5
        HOST_MSG = "次の問題まで"
        lbl_status["text"] = HOST_MSG
        data = HOST.read_score()
        alist = []
        msg = ""
        for i in data:
            alist.append(data[i][3])
        for i in range(len(alist)):
            msg += "チーム"+str(i+1)+" "+format(alist[i] * 100, "7.3f")+"%\n"
        lbl_rank["text"] = msg
        quiz_next()
        return
    
    TIMER -= 1
    
    lbl_Timer["text"] = TIMER
    lbl_Timer.after(1000, quiz_trueans)

def quiz_next():
    global nowquiz, Quiz_txt, HOST_MSG, TIMER
    if TIMER == 0:
        TIMER = 15
        nowquiz += 1
        if nowquiz == len(Quiz_List) + 1:
            flm_Quiz.destroy()
            Win_Result()
            return
        lbl_Num["text"] = nowquiz
        Quiz_txt = Quiz_List[nowquiz-1]["question"]
        if len(Quiz_txt) > 23:
            Quiz_txt=Quiz_txt[:23]+"\n"+Quiz_txt[23:]
        lbl_Quiz["text"] = Quiz_txt
        HOST_MSG = "回答締め切りまで"
        lbl_status["text"] = HOST_MSG
        lbl_QTrue.place(x=240, y=240, anchor=tk.CENTER)
        lbl_QFalse.place(x=720, y=240, anchor=tk.CENTER)
        data = HOST.read_state()
        data["time"] = time.time()
        HOST.write_state(data)
        quiz_timer()
        return
    TIMER -= 1
    lbl_Timer["text"] = TIMER
    lbl_Timer.after(1000, quiz_next)

def step_next():
    pass

def get_client():
    client_data = HOST.read_client()
    if (len(client_data) != int(client_all)):
        lbl_Cli["text"] = str(len(client_data)) + " / " + str(client_all)
        lbl_Cli.after(5000, get_client)
    else:
        btn_ok["state"] = "active"
        lbl_Msg["text"] = "準備が完了しました"
        lbl_Cli["text"] = str(len(client_data)) + " / " + str(client_all)

def get_start():
    data = CLIENT.read_state()
    if data["state_code"] == 20:
        root.destroy()
    else:
        flm_Step.after(10000, get_start)

def sub_get():
    with open("error.log", "r") as f:
        data = f.read()
    if data:
        if data=="-1":
            win_quit()
        else:
            print(data)
    else:
        flm_Camera.after(1000, sub_get)

"""
    ウィンドウ一覧
                """
def Win_Mode():
    """
    初期画面
    --------
    ホストモードかクライアントモードか選択する

    選択肢
    --------
    ホスト: -> Win_CNum()
    クライアント:Win_Load() -> Win_Camera()
    """
    global flm_Mode
    flm_Mode = tk.Frame(root)
    flm_Mode.pack(expand=1, fill=tk.BOTH)
    lbl_Title = tk.Label(flm_Mode, text="モードを選択してください", font=("Arial", 30))
    lbl_Title.place(x=480, y=135, anchor=tk.CENTER)
    btn_host = tk.Button(flm_Mode, text="ホスト", font=("Arial", 30), command=mode_host)
    btn_host.place(x=240, y=340, anchor=tk.CENTER)
    btn_client = tk.Button(flm_Mode, text="クライアント", font=("Arial", 30), command=mode_client)
    btn_client.place(x=720, y=340, anchor=tk.CENTER)
    btn_make = tk.Button(flm_Mode, text="クイズ作成", font=("Arial", 30), command=mode_make)
    btn_make.place(x=480, y=450, anchor=tk.CENTER)

""" ホスト側ウィンドウ """
def Win_CNum():
    """
    クライアント数指定
    --------
    クライアント数をSpinboxで指定

    未解決
    --------
    * Spinboxの上下ボタンを1単位で変更する

    元画面
    --------
    Win_Mode()

    選択肢
    --------
    決定: -> エラー時:Win_Error() 正常時:Win_Manual()
    """
    global flm_CNum, spn_Num
    flm_CNum = tk.Frame(root)
    flm_CNum.pack(expand=1, fill=tk.BOTH)
    lbl_Msg = tk.Label(flm_CNum, text="クライアント(クイズに参加する会場)\nの数を入力してください", font=("Arial", 30))
    lbl_Msg.place(x=480, y=135, anchor=tk.CENTER)
    spn_Num = tk.Spinbox(flm_CNum, from_=1, to=10, increment=10, font=("Arial", 20))
    spn_Num.place(x=480, y=270, anchor=tk.CENTER, height=50, width=100)
    btn_ok = tk.Button(flm_CNum, text="決定", font=("Arial", 30), command=cnum_ok)
    btn_ok.place(x=480, y=350, anchor=tk.CENTER)

def Win_Error():
    """
    ホスト用エラー
    --------
    Win_CNum()の「決定」をクリックしたが、他サーバーがすでに起動している場合に表示

    元画面
    --------
    Win_CNum()

    未解決
    --------
    * Win_Error2()と名前を差別化する

    選択肢
    --------
    ホーム画面に戻る: -> Win_Mode()
    """
    global flm_Error
    flm_Error = tk.Frame(root)
    flm_Error.pack(expand=1, fill=tk.BOTH)
    lbl_Error = tk.Label(flm_Error, text="サーバーは一つしか起動できません", font=("Arial", 30))
    lbl_Error.place(x=480, y=135, anchor=tk.CENTER)
    btn_back = tk.Button(flm_Error, text="ホーム画面に戻る", font=("Arial", 30), command=error_back)
    btn_back.place(x=720, y=405, anchor=tk.CENTER)

def Win_Manual():
    """
    マニュアル&json選択
    --------
    マニュアルを表示し、クイズ用jsonファイルを選択する

    元画面
    --------
    Win_CNum()

    未解決
    --------

    選択肢
    --------
    次へ: -> Win_HWait()
    """
    global flm_Manual
    flm_Manual = tk.Frame(root)
    flm_Manual.pack(expand=1, fill=tk.BOTH)
    lbl_Manual01 = tk.Label(flm_Manual, text="①Zoomで会議を開始", font=("Arial", 30))
    lbl_Manual01.place(x=480, y=108, anchor=tk.CENTER)
    lbl_Manual02 = tk.Label(flm_Manual, text="②このウィンドウを画面共有", font=("Arial", 30))
    lbl_Manual02.place(x=480, y=216, anchor=tk.CENTER)
    lbl_Manual03 = tk.Label(flm_Manual, text="③クイズデータが入ったjsonファイルを選択", font=("Arial", 30))
    lbl_Manual03.place(x=480, y=324, anchor=tk.CENTER)
    btn_dia = tk.Button(flm_Manual, text="ファイルを選択", font=("Arial", 30), command=manual_dia)
    btn_dia.place(x=240, y=432, anchor=tk.CENTER)
    btn_next = tk.Button(flm_Manual, text="次へ", font=("Arial", 30), command=manual_next)
    btn_next.place(x=720, y=432, anchor=tk.CENTER)

def Win_HWait():
    """
    クライアント待機
    --------
    準備が完了したクライアント数を表示し、全員が集まるまで待機する

    元画面
    --------
    Win_Manual()

    未解決
    --------

    選択肢
    --------
    開始: -> Win_Quiz()
    """
    global flm_HWait, lbl_Cli, lbl_Msg, btn_ok
    flm_HWait = tk.Frame(root)
    flm_HWait.pack(expand=1, fill=tk.BOTH)
    lbl_Msg = tk.Label(flm_HWait, text="クライアントを待っています...", font=("Arial", 30))
    lbl_Msg.place(x=480, y=135, anchor=tk.CENTER)
    lbl_Cli = tk.Label(flm_HWait, text="0 / "+str(client_all), font=("Arial", 30))
    lbl_Cli.place(x=480, y=270, anchor=tk.CENTER)
    btn_ok = tk.Button(flm_HWait, text="開始", font=("Arial", 30), command=hwait_ok, state="disable")
    btn_ok.place(x=480, y=350, anchor=tk.CENTER)
    get_client()    

def Win_Quiz():
    """
    クイズ出題
    --------
    クイズの問題、制限時間、得点等を表示する

    元画面
    --------
    Win_HWait()

    未解決
    --------

    選択肢
    --------
    (全問終了): -> Win_Result()
    """
    global flm_Quiz, nowquiz, lbl_QTrue, lbl_QFalse, lbl_Timer, TIMER, HOST_MSG, lbl_status, Quiz_txt, lbl_Quiz, lbl_Num, lbl_rank
    HOST_MSG = "回答締め切りまで"
    TIMER = 15
    Quiz_txt = Quiz_List[nowquiz-1]["question"]
    if len(Quiz_txt) > 23:
        Quiz_txt=Quiz_txt[:23]+"\n"+Quiz_txt[23:]
    data = HOST.read_state()
    data["time"] = time.time()
    HOST.write_state(data)
    flm_Quiz = tk.Frame(root)
    flm_Quiz.pack(expand=1, fill=tk.BOTH)
    lbl_Num = tk.Label(flm_Quiz, text=nowquiz, font=("Arial", 30))
    lbl_Num.place(x=100, y=500, anchor=tk.CENTER)
    lbl_Quiz = tk.Label(flm_Quiz, text=Quiz_txt, font=("Arial", 30))
    lbl_Quiz.place(x=480, y=80, anchor=tk.CENTER)
    img_true = tk.PhotoImage(file="image/true.png")
    lbl_QTrue = tk.Label(flm_Quiz, width=200, height=200, image=img_true)
    lbl_QTrue.photo = img_true
    lbl_QTrue.place(x=240, y=240, anchor=tk.CENTER)
    img_false = tk.PhotoImage(file="image/false.png")
    lbl_QFalse = tk.Label(flm_Quiz, width=200, height=200, image=img_false)
    lbl_QFalse.photo = img_false
    lbl_QFalse.place(x=720, y=240, anchor=tk.CENTER)
    lbl_Timer = tk.Label(flm_Quiz, text=TIMER, font=("Arial", 30))
    lbl_Timer.place(x=480, y=240, anchor=tk.CENTER)
    lbl_Timer.after(1000, quiz_timer)
    lbl_status = tk.Label(flm_Quiz, text=HOST_MSG, font=("Arial", 30))
    lbl_status.place(x=480, y=180, anchor=tk.CENTER)
    lbl_rank = tk.Label(flm_Quiz, text="", font=("Arial", 30))
    lbl_rank.place(x=480, y=440, anchor=tk.CENTER)

def Win_Result():
    """
    クイズの総合結果
    --------
    クイズの勝者を表示する

    元画面
    --------
    Win_Quiz()

    未解決
    --------

    選択肢
    --------
    終了: -> sys.exit()
    """
    global flm_Result

    HOST.write_state({"state_code": 0})
    
    data = HOST.read_score()
    alist = []
    for i in data:
        alist.append(data[i][3])
    first = alist.index(max(alist))
    
    flm_Result = tk.Frame(root)
    flm_Result.pack(expand=1, fill=tk.BOTH)
    lbl_Manual01 = tk.Label(flm_Result, text="結果", font=("Arial", 30))
    lbl_Manual01.place(x=480, y=50, anchor=tk.CENTER)
    lbl_Manual02 = tk.Label(flm_Result, text="チーム"+str(first+1)+"の勝ち", font=("Arial", 30))
    lbl_Manual02.place(x=480, y=150, anchor=tk.CENTER)
    lbl_Manual02 = tk.Label(flm_Result, text="Zoomから退出してかまいません", font=("Arial", 30))
    lbl_Manual02.place(x=480, y=350, anchor=tk.CENTER)
    btn_next = tk.Button(flm_Result, text="終了", font=("Arial", 30), command=sys.exit)
    btn_next.place(x=720, y=450, anchor=tk.CENTER)

""" クライアント側ウィンドウ"""
def Win_Error2():
    """
    クライアント用エラー
    --------
    Win_Mode()の「クライアント」をクリックしたが、サーバーが起動していない場合に表示

    未解決
    --------
    * Win_Error2()という名前をどうにかする

    元画面
    --------
    Win_Mode()

    選択肢
    --------
    ホーム画面に戻る: -> Win_Mode()
    """
    global flm_Error2
    flm_Error2 = tk.Frame(root)
    flm_Error2.pack(expand=1, fill=tk.BOTH)
    lbl_Error2 = tk.Label(flm_Error2, text="ホストが開始されていません", font=("Arial", 30))
    lbl_Error2.place(x=480, y=135, anchor=tk.CENTER)
    btn_back2 = tk.Button(flm_Error2, text="ホーム画面に戻る", font=("Arial", 30), command=error_back2)
    btn_back2.place(x=720, y=405, anchor=tk.CENTER)

def Win_Camera():
    """
    カメラテスト
    --------
    camera_main.pyをサブプロセスで開始し、エラーを検知する

    未解決
    --------
    

    元画面
    --------
    Win_Mode()

    選択肢
    --------
    次へ: -> Win_Step()
    """
    global flm_Camera, cam_pro
    flm_Camera = tk.Frame(root)
    flm_Camera.pack(expand=1, fill=tk.BOTH)
    lbl_Step01 = tk.Label(flm_Camera, text="カメラのチェック中です...", font=("Arial", 30))
    lbl_Step01.place(x=480, y=108, anchor=tk.CENTER)
    btn_next = tk.Button(flm_Camera, text="次へ", font=("Arial", 30), command=camera_next)
    btn_next.place(x=720, y=450, anchor=tk.CENTER)
    cam_pro = sp.Popen(["python", "camera_main.py"], shell=True)
    cam_err()

def Win_Step():
    """
    クライアント側マニュアル
    --------
    マニュアルを表示し、クイズデータを読み込み、サーバーのクイズ開始を待機する

    未解決
    --------
    

    元画面
    --------
    Win_Mode()

    選択肢
    --------
    (クイズ開始後):
    """
    global flm_Step, Quiz_List
    Quiz_List = CLIENT.read_quiz()
    flm_Step = tk.Frame(root)
    flm_Step.pack(expand=1, fill=tk.BOTH)
    lbl_Step01 = tk.Label(flm_Step, text="①Zoomで会議に参加", font=("Arial", 30))
    lbl_Step01.place(x=480, y=108, anchor=tk.CENTER)
    lbl_Step02 = tk.Label(flm_Step, text="②カメラウィンドウを画面共有", font=("Arial", 30))
    lbl_Step02.place(x=480, y=216, anchor=tk.CENTER)
    lbl_Step03 = tk.Label(flm_Step, text="チーム番号は"+str(team_num)+"番です", font=("Arial", 30))
    lbl_Step03.place(x=480, y=324, anchor=tk.CENTER)
    get_cl()

def Ans_Send():
    """
    回答結果集計
    --------
    camera_main.pyが出力したuserInfo.jsonを読み込み、google sheetsに出力する

    未解決
    --------
    すべて

    元画面
    --------
    Win_Mode()

    選択肢
    --------
    (クイズ終了後):camera_main.pyを終了する
    """
    datab = 0

    if mode != 1:
        sys.exit()
    for i in range(len(Quiz_List)):
        while 1:
            data = CLIENT.read_state()
            if datab != data["time"]:
                deltatime = time.time() - data["time"]
                print(deltatime)
                break
            else:
                time.sleep(10)

        time.sleep(20 - deltatime)
        with open("userInfo.json", "r") as f:
            ansdata = json.load(f)
        CLIENT.write_score(ansdata, Quiz_List[i]["answer"])
        with open("camera_cmd.txt", "w") as f:
            if Quiz_List[i]["answer"] == 1:
                f.write("m")
            else:
                f.write("v")
        time.sleep(10)
        datab = data["time"]
        with open("camera_cmd.txt", "w") as f:
            f.write("t")

"""
    実行
        """
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("960x540")

    msg = ""
    mode = None
    nowquiz = 1
    quizpath = None
    TIMER = None
    HOST_MSG = None
    Quiz_txt = None
    Win_Mode()
    root.protocol("WM_DELETE_WINDOW", win_quit)
    root.mainloop()

