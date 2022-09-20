import gspread
import json
from datetime import datetime
import os.path

# このpythonファイルが置いてあるディレクトリ
path = os.path.dirname(os.path.abspath(__file__))

client_id=None

# Google Drive API
client = gspread.service_account(filename=path+'/sodium-hue-361405-237068a500a2.json')
spr = client.open("MVP")
status_sheet = spr.worksheet("status")
score_sheet = spr.worksheet("score")
quiz_sheet = spr.worksheet("quiz")


def init():
    pass


def load_status():
    data = status_sheet.get_values()
    return {d[0]: d[1] for d in data if d[0]}

def load_score():
    return score_sheet.get_values()

def load_quiz():
    return quiz_sheet.get_all_records()


def write_score(data: dict, correct_ans: bool) -> float:
    answers = list(data.values())

    cells = score_sheet.range(client_id, 1, client_id, 4)

    correct = cells[1].numeric_value+answers.count(correct_ans)
    sum = cells[2].numeric_value+len(answers)
    rate = correct/sum

    cells[0].value = datetime.now().isoformat()
    cells[1].value = correct
    cells[2].value = sum
    cells[3].value = rate

    score_sheet.update_cells(cells)

    return rate

# with open(path+"/ans.json") as f:
#    data=json.load(f)
#    write_score(data,1,False)
