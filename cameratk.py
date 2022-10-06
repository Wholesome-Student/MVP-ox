import tkinter
import cv2
import PIL.ImageTk
 
app = tkinter.Tk()
app.title("Python-Camera")
app.geometry("640x610")
 
canvas1 = tkinter.Canvas(app, width= 640, height=480)
canvas1.pack()
 
rb_v = tkinter.IntVar(value=0)
tkinter.Radiobutton(app, value=0, variable=rb_v
                    , text='カラー').place(x=10, y=485)
tkinter.Radiobutton(app, value=1, variable=rb_v
                    , text='グレースケール').place(x=80, y=485)
tkinter.Radiobutton(app, value=2, variable=rb_v
                    , text='エッジ検出').place(x=200, y=485)
 
s1_v = tkinter.IntVar(value=50)
s2_v = tkinter.IntVar(value=100)
threshold1 =50
threshold2 =100
def scroll(event=None):
    global threshold1
    global threshold2
    threshold1 = s1_v.get()
    threshold2 = s2_v.get()
tkinter.Scale(app, variable=s1_v, command=scroll
              , orient='horizontal', length=580
              , to=500, resolution=10,).place(x=50, y=510)
tkinter.Scale(app, variable=s2_v, command=scroll
              , orient='horizontal', length=580
              , to=500, resolution=10,).place(x=50, y=555)
tkinter.Label(app, text='閾値1').place(x=0, y=530)
tkinter.Label(app, text='閾値2').place(x=0, y=575)
 
capture = cv2.VideoCapture(1)
def camera():
    ret, frame = capture.read()    
    if rb_v.get() == 0:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    else:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if rb_v.get() == 2:
            frame = cv2.Canny(frame, threshold1, threshold2)  
    app.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame)) 
    canvas1.create_image(0,0, image= app.photo, anchor = 'nw')
    app.after(50, camera)
     
camera()
app.mainloop()