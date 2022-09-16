""" Library """
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import json

root = tk.Tk()
root.geometry("960x540")

""" button's command """
def title_start():
    flm_Title.destroy()
    Win_Start()

def title_make():
    flm_Title.destroy()
    Win_Make()

def make_true():
    print("O")

def make_false():
    print("X")

def make_cancel():
    flm_Make.destroy()
    Win_Title()

def make_save():
    txtdata = txt_Question.get('1.0', 'end').rstrip("\n")
    txtlist = [{"question": txtdata, "ans": "O"}]
    jsondata = json.dumps(txtlist, indent=4, ensure_ascii=False)
    print(jsondata)

def start_back():
    flm_Start.destroy()
    Win_Title()

def start_everyone():
    flm_Start.destroy()
    Win_Quiz()

def start_dir():
    global jsondata
    filepath = tk.filedialog.askopenfilename(initialdir = "")
    with open(filepath, 'r') as j:
        jsondata = json.load(j)
    print(jsondata)
    lbl_path["text"] = filepath

""" windows """
def Win_Title():
    global flm_Title
    flm_Title = tk.Frame(root)
    flm_Title.pack(expand=1, fill=tk.BOTH)
    lbl_Title = tk.Label(flm_Title, text="Maru Vatu Possible", font=("Arial", 30))
    lbl_Title.place(x=480, y=135, anchor=tk.CENTER)
    btn_start = tk.Button(flm_Title, text="Start", font=("Arial", 30), command=title_start)
    btn_start.place(x=240, y=405, anchor=tk.CENTER)
    btn_quiz = tk.Button(flm_Title, text="Make Quiz", font=("Arial", 30), command=title_make)
    btn_quiz.place(x=720, y=405, anchor=tk.CENTER)

def Win_Make():
    global flm_Make, txt_Question
    flm_Make = ttk.Frame(root)
    flm_Make.pack(expand=1, fill=tk.BOTH)
    lbl_Title = tk.Label(flm_Make, text="Make Quiz", font=("Arial", 30))
    lbl_Title.place(x=480, y=67.5, anchor=tk.CENTER)
    lbl_Question = tk.Label(flm_Make, text="Question", font=("Arial", 15))
    lbl_Question.place(x=120, y=202.5, anchor=tk.CENTER)
    txt_Question = tk.Text(flm_Make, height=3, width = 50)
    txt_Question.place(x=600, y=202.5, anchor=tk.CENTER)
    
    lbl_Answer = tk.Label(flm_Make, text="Answer", font=("Arial", 15))
    lbl_Answer.place(x=120, y=337.5, anchor=tk.CENTER)
    btn_True = tk.Button(flm_Make, text="O", command=make_true)
    btn_True.place(x=576, y=337.5, anchor=tk.CENTER)
    btn_False = tk.Button(flm_Make, text="X", command=make_false)
    btn_False.place(x=768, y=337.5, anchor=tk.CENTER)
    btn_Cancel = tk.Button(flm_Make, text="Cancel", command=make_cancel)
    btn_Cancel.place(x=320, y=472.5, anchor=tk.CENTER)
    btn_Save = tk.Button(flm_Make, text="Save", command=make_save)
    btn_Save.place(x=640, y=472.5, anchor=tk.CENTER)

def Win_Start():
    global flm_Start, lbl_path
    flm_Start = ttk.Frame(root)
    flm_Start.pack(expand=1, fill=tk.BOTH)
    spn_var = 0
    lbl_Title = tk.Label(flm_Start, text="Start", font=("Arial", 30))
    lbl_Title.place(x=480, y=67.5, anchor=tk.CENTER)
    lbl_Setting = tk.Label(flm_Start, text="Setting", font=("Arial", 15))
    lbl_Setting.place(x=120, y=202.5, anchor=tk.CENTER)
    spn_quiz = ttk.Spinbox(flm_Start, format="%3d", from_=1, to=999, textvariable=spn_var, font=("Arial", 15))
    spn_quiz.place(x=600, y=202.5, anchor=tk.CENTER)
    lbl_theme = tk.Label(flm_Start, text="Theme", font=("Arial", 15))
    lbl_theme.place(x=120, y=337.5, anchor=tk.CENTER)
    btn_dir = tk.Button(flm_Start, text="Select Dir", font=("Arial", 15), command=start_dir)
    btn_dir.place(x=360, y=337.5, anchor=tk.CENTER)
    lbl_path = tk.Label(flm_Start, text="", font=("Arial", 15))
    lbl_path.place(x=720, y=337.5, anchor=tk.CENTER)
    btn_back = tk.Button(flm_Start, text="Back", command=start_back, font=("Arial", 15))
    btn_back.place(x=240, y=472.5, anchor=tk.CENTER)
    btn_Everyone = tk.Button(flm_Start, text="Everyone", font=("Arial", 15), command=start_everyone)
    btn_Everyone.place(x=480, y=472.5, anchor=tk.CENTER)
    btn_Survival = tk.Button(flm_Start, text="Survival", font=("Arial", 15))
    btn_Survival.place(x=720, y=472.5, anchor=tk.CENTER)

def Win_Quiz():
    global flm_Quiz
    flm_Quiz = ttk.Frame(root)
    flm_Quiz.pack(expand=1, fill=tk.BOTH)
    lbl_Quiz = tk.Label(flm_Quiz, borderwidth = 3, relief="solid", text="What is this question's contents?", font=("Arial", 20))
    lbl_Quiz.place(x=480, y=135, anchor=tk.CENTER)
    lbl_True = tk.Label(flm_Quiz, text="O", font=("Arial", 100))
    lbl_True.place(x=240, y=405, anchor=tk.CENTER)
    lbl_False = tk.Label(flm_Quiz, text="X", font=("Arial", 100))
    lbl_False.place(x=720, y=405, anchor=tk.CENTER)

Win_Title()
root.mainloop()