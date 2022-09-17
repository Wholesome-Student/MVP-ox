import gspread
import json
from datetime import datetime
import os.path

#このpythonファイルが置いてあるディレクトリ
path=os.path.dirname(os.path.abspath(__file__))

#Google Drive API
client = gspread.service_account(filename=path+'/sodium-hue-361405-237068a500a2.json')
spr = client.open("MVP")
status_sheet = spr.worksheet("status")
score_sheet = spr.worksheet("score")
quiz_sheet = spr.worksheet("quiz")

def load_status():
    data=status_sheet.get_values() 
    return {d[0]:d[1] for d in data if d[0]}

def load_score():
    return score_sheet.get_values()

def load_quiz():
    return quiz_sheet.get_values()

def write_score(data,client_id:int,correct_ans:bool):
    answers=list(data.values())
    correct=answers.count(correct_ans)
    sum=len(answers)

    cells = score_sheet.range(client_id, 1, client_id, 4)
    cells[0].value = datetime.now().isoformat()
    cells[1].value = correct
    cells[2].value = sum
    cells[3].value = correct/sum

    score_sheet.update_cells(cells)

#with open(path+"/ans.json") as f:
#    data=json.load(f)
#    write_score(data,1,False)