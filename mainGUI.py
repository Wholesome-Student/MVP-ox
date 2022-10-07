"""
HOST: Mode -> CNum -> Manual -> Quiz -> Result
CLIENT: Step

"""


""" Library """
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import json
import sprapi as sa
import time
import threading
import sys
import cv2
import subprocess as sp

root = tk.Tk()
root.geometry("960x540")

mode = None
nowquiz = 1
quizpath = None
TIMER = None
HOST_MSG = None
Quiz_txt = None

with open("camera_cmd.txt", "w") as f:
    f.write("")

def win_quit():
    if mode == 0:
        data = HOST.read_state()
        data["state_code"] = 0
        data["time"] = -1
        HOST.write_state(data)
    elif mode == 1:
        with open("camera_main.py", "w") as f:
            f.write("q")
    sys.exit()

def host():
    global HOST, mode
    try:
        HOST = sa.MVPHost(client_Num)
    except RuntimeError:
        flm_Load.destroy()
        Win_Error()
    else:
        flm_Load.destroy()
        Win_Manual()
        mode = 0

def client():
    global CLIENT, mode, team_num
    try:
        CLIENT = sa.MVPClient()
        team_num = CLIENT.client_id
    except:
        flm_Load.destroy()
        Win_Error2()
    else:
        flm_Load.destroy()
        Win_Step()
        mode = 1
    
def readjson():
    global quizdata
    with open(quizpath, "r", encoding="utf-8") as f:
        quizdata = json.load(f)


        

""" call back """
def host_start():
    th = threading.Thread(target=host)
    th.start()

def client_start():
    th = threading.Thread(target=client)
    th.start()

def get_cl():
    th = threading.Thread(target=get_start)
    th.start()

""" button's command """
def mode_host():
    flm_Mode.destroy()
    Win_CNum()

def mode_client():
    global flm_Load
    flm_Mode.destroy()
    flm_Load = tk.Frame(root)
    flm_Load.pack(expand=1, fill=tk.BOTH)
    lbl_Load = tk.Label(flm_Load, text="Loading...", font=("Arial", 30))
    lbl_Load.place(x=480, y=135, anchor=tk.CENTER)
    client_start()

def mode_make():
    sp.Popen(["python", "make_quiz.py"], shell=True)
    root.destroy()

def error_back():
    flm_Error.destroy()
    Win_Mode()

def error_back2():
    flm_Error2.destroy()
    Win_Mode()

def count_cl():
    global client_all
    client_all = spn_Num.get()
    return client_all

def cnum_ok():
    global flm_Load, client_Num
    client_Num = count_cl()
    flm_CNum.destroy()
    flm_Load = tk.Frame(root)
    flm_Load.pack(expand=1, fill=tk.BOTH)
    lbl_Load = tk.Label(flm_Load, text="Loading...", font=("Arial", 30))
    lbl_Load.place(x=480, y=135, anchor=tk.CENTER)
    host_start()

def manual_dia():
    global quizpath
    typ = [('クイズファイル','*.json')] 
    dir = './'
    quizpath = filedialog.askopenfilename(filetypes = typ, initialdir = dir)

def manual_next():
    global Quiz_List
    flm_Manual.destroy()
    if quizpath != None:
        readjson()
        HOST.write_quiz(quizdata)
    Quiz_List = HOST.read_quiz()
    Win_HWait()

def hwait_ok():
    flm_HWait.destroy()
    data = HOST.read_state()
    data["state_code"] = 20
    HOST.write_state(data)
    Win_Quiz()

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

msg = ""
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
    global Quiz_List
    #flm_Step.destroy()
    Quiz_List = CLIENT.read_quiz()
    get_cl()

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



""" window """
def Win_Mode():
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

def Win_Error():
    global flm_Error
    flm_Error = tk.Frame(root)
    flm_Error.pack(expand=1, fill=tk.BOTH)
    lbl_Error = tk.Label(flm_Error, text="サーバーは一つしか起動できません", font=("Arial", 30))
    lbl_Error.place(x=480, y=135, anchor=tk.CENTER)
    btn_back = tk.Button(flm_Error, text="ホーム画面に戻る", font=("Arial", 30), command=error_back)
    btn_back.place(x=720, y=405, anchor=tk.CENTER)

def Win_Error2():
    global flm_Error2
    flm_Error2 = tk.Frame(root)
    flm_Error2.pack(expand=1, fill=tk.BOTH)
    lbl_Error2 = tk.Label(flm_Error2, text="ホストが開始されていません", font=("Arial", 30))
    lbl_Error2.place(x=480, y=135, anchor=tk.CENTER)
    btn_back2 = tk.Button(flm_Error2, text="ホーム画面に戻る", font=("Arial", 30), command=error_back2)
    btn_back2.place(x=720, y=405, anchor=tk.CENTER)

def Win_Manual():
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

def Win_CNum():
    global flm_CNum, spn_Num
    flm_CNum = tk.Frame(root)
    flm_CNum.pack(expand=1, fill=tk.BOTH)
    lbl_Msg = tk.Label(flm_CNum, text="クライアント(クイズに参加する会場)\nの数を入力してください", font=("Arial", 30))
    lbl_Msg.place(x=480, y=135, anchor=tk.CENTER)
    spn_Num = tk.Spinbox(flm_CNum, from_=1, to=10, increment=10, font=("Arial", 20))
    spn_Num.place(x=480, y=270, anchor=tk.CENTER, height=50, width=100)
    btn_ok = tk.Button(flm_CNum, text="決定", font=("Arial", 30), command=cnum_ok)
    btn_ok.place(x=480, y=350, anchor=tk.CENTER)

def Win_HWait():
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

def Win_Step():
    global flm_Step
    flm_Step = tk.Frame(root)
    flm_Step.pack(expand=1, fill=tk.BOTH)
    lbl_Step01 = tk.Label(flm_Step, text="①Zoomで会議に参加", font=("Arial", 30))
    lbl_Step01.place(x=480, y=108, anchor=tk.CENTER)
    lbl_Step02 = tk.Label(flm_Step, text="②カメラウィンドウを画面共有", font=("Arial", 30))
    lbl_Step02.place(x=480, y=216, anchor=tk.CENTER)
    lbl_Step03 = tk.Label(flm_Step, text="チーム番号は"+str(team_num)+"番です", font=("Arial", 30))
    lbl_Step03.place(x=480, y=324, anchor=tk.CENTER)
    btn_next = tk.Button(flm_Step, text="次へ", font=("Arial", 30), command=step_next)
    btn_next.place(x=720, y=432, anchor=tk.CENTER)
    sp.Popen(["python", "camera_main.py"], shell=True)


def Win_Quiz():
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
    global flm_Result
    
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

Win_Mode()
root.protocol("WM_DELETE_WINDOW", win_quit)
root.mainloop()

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
