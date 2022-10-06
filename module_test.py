import numpy as np
import cv2
from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol
import json
import mvp_qr

ans = False
users = {}
matchAns = False
playerCount = 0
matchCount = 0

#Webカメラの読み込み
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FPS, 5)
#出力ウィンドウの設定
cap.set(3,1280)
cap.set(3,960)

while True:
    ret,frame = cap.read()
    pil_frame = Image.fromarray(frame[:,:,::-1])

    d = decode(cv2.cvtColor(frame, cv2.COLOR_RGBA2GRAY), symbols=[ZBarSymbol.QRCODE])
    for code in d:
        userInfo = mvp_qr.qr_decode(code.data.decode("utf-8"))
        if userInfo['ans']!=None:
            users[userInfo['id']] = userInfo['ans']
            with open("userInfo.json", "w") as writeJsonFile:
                json.dump(users, writeJsonFile, ensure_ascii=False, indent=2)

            x, y, w, h = code.rect

            playerCount += 1

            if not matchAns:
                particle = Image.open('image/particle.png')
            else:
                if userInfo['ans'] == ans:
                    particle = Image.open('image/oukan.png')
                    matchCount += 1
                else:
                    particle = Image.open('image/bom.png')
            particle = particle.resize((w * 2, h * 2))

            pil_frame.paste(particle, (int(x - w / 2), int(y - h / 2)), particle)
            # cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 3)
    frame = np.asarray(pil_frame)[:,:,::-1]

    matchCount = 0
    playerCount = 0
    cv2.imshow("MaruVatuPossible", frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('a'):
        matchAns = True
    elif key == ord('t'):
        matchAns = False
        users = {}
    elif key == ord('m'):
        ans = True
    elif key == ord('v'):
        ans = False