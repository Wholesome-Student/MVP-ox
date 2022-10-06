import json
import tkinter as tk
from tkinter import filedialog,messagebox

quizzes=[]

root=tk.Tk()
root.geometry("800x600")
root.title("問題作成")

main_frm=tk.Frame(root)
edit_frm=tk.Frame(root)

ans_var=tk.BooleanVar()
index=tk.END

def reset():
    quiz_box.delete(0, tk.END)
    [quiz_box.insert(tk.END, quiz[0]) for quiz in quizzes]

def editer(idx):
    global index
    index=idx
    edit_frm.grid(column=0,row=0,sticky=tk.NSEW,padx=5,pady=5)

def set_quiz():
    ques=ques_box.get().strip()
    ans=ans_var.get()
    if not ques:
        messagebox.showwarning("","問題文が空です")
    else:
        if index!=tk.END:
            quizzes[index]=[ques,ans]
        else:
            quizzes.append([ques,ans])
        reset()
        end_edit()

def end_edit():
    ques_box.delete(0, tk.END)
    edit_frm.grid_forget()

def add_quiz():
    ans_var.set(True)
    editer(tk.END)

def edit_quiz():
    idx=quiz_box.curselection()
    if idx:
        ques_box.insert(0,quizzes[idx[0]][0])
        ans_var.set(quizzes[idx[0]][1])
        editer(idx[0])

def del_quiz():
    idx=quiz_box.curselection()
    if idx:
        quizzes.pop(idx[0])
        reset()

def open_file():
    global quizzes
    typ = [("クイズファイル","*.json")] 
    dir = "./"
    quizpath = filedialog.askopenfilename(filetypes = typ, initialdir = dir)
    try:
        with open(quizpath, "r", encoding="utf-8") as f:
            quizdata = json.load(f)
        quizzes=[[quiz["question"],quiz["answer"]] for quiz in quizdata]
    except Exception as e:
        messagebox.showerror("file error","ファイルを開けませんでした")
    else:
        reset()

def save_file():
    typ = [("クイズファイル","*.json")] 
    dir = "./"
    quizpath = filedialog.asksaveasfilename(filetypes = typ, initialdir = dir)
    try:
        with open(quizpath, "w", encoding="utf-8") as f:
            json.dump([{"id":i,"question":quiz[0],"answer":quiz[1]} for i,quiz in enumerate(quizzes)],f,ensure_ascii=False,indent=4)
    except Exception as e:
        print(e)
        messagebox.showerror("file error","保存に失敗しました")
    else:
        messagebox.showinfo("save","保存しました")

quiz_box=tk.Listbox(main_frm,background="#FFFFFF", selectmode="single")
ybar = tk.Scrollbar(main_frm,orient=tk.VERTICAL)
ybar.config(command=quiz_box.yview)
quiz_box.config(yscrollcommand=ybar.set)
manual=tk.Label(main_frm,text="問題を追加するか、問題を選択して編集および削除します")
load_btn=tk.Button(main_frm,text="ファイルを開く",command=open_file)
write_btn=tk.Button(main_frm,text="ファイルを保存",command=save_file)
add_btn=tk.Button(main_frm,text="追加",command=add_quiz)
edit_btn=tk.Button(main_frm,text="編集",command=edit_quiz)
del_btn=tk.Button(main_frm,text="削除",command=del_quiz)
ques_label=tk.Label(edit_frm,text="[問題文]")
ques_box=tk.Entry(edit_frm)
ans_label=tk.Label(edit_frm,text="[正答]")
maru_btn=tk.Radiobutton(edit_frm,text="〇",value=True,variable=ans_var)
vatu_btn=tk.Radiobutton(edit_frm,text="×",value=False,variable=ans_var)
set_btn=tk.Button(edit_frm,text="確定",command=set_quiz)
cancel_btn=tk.Button(edit_frm,text="キャンセル",command=end_edit)
manual.grid(row=0,column=0,columnspan=9,padx=5,pady=5)
quiz_box.grid(row=1,column=0,columnspan=9,sticky=tk.NSEW,padx=5,pady=5)
ybar.grid(row=1,column=9,sticky=tk.NS)
load_btn.grid(row=2,column=0,padx=5,pady=5)
write_btn.grid(row=2,column=1,padx=5)
add_btn.grid(row=2,column=6,padx=5)
edit_btn.grid(row=2,column=7,padx=5)
del_btn.grid(row=2,column=8,columnspan=2,padx=5)
main_frm.columnconfigure(3,weight=1)
main_frm.rowconfigure(1,weight=1)
main_frm.grid(column=0,row=0,sticky=tk.NSEW,padx=5,pady=5)
ques_label.grid(row=0,column=1,columnspan=2,padx=5,pady=5)
ques_box.grid(row=1,column=0,columnspan=4,sticky=tk.EW,padx=5,pady=5)
ans_label.grid(row=2,column=1,columnspan=2,padx=5,pady=15)
maru_btn.grid(row=3,column=1,padx=5)
vatu_btn.grid(row=3,column=2,padx=5)
set_btn.grid(row=4,column=1,columnspan=2,padx=30)
cancel_btn.grid(row=5,column=1,columnspan=2,padx=5)
edit_frm.columnconfigure(0,weight=1)
edit_frm.columnconfigure(3,weight=1)
root.columnconfigure(0,weight=1)
root.rowconfigure(0,weight=1)
root.mainloop()