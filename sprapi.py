import gspread
import json
from datetime import datetime
import os.path

# このpythonファイルが置いてあるディレクトリ
path = os.path.dirname(os.path.abspath(__file__))

client_id = None

# Google Drive API
client = gspread.service_account(filename=path+"/sodium-hue-361405-237068a500a2.json")
spr = client.open("MVP")
status_sheet = spr.worksheet("status")
score_sheet = spr.worksheet("score")
quiz_sheet = spr.worksheet("quiz")


def init():
    pass


def read_status():
    data = status_sheet.get_values()
    return {row[0]: row[1] for row in data if row[0]}

def read_score():
    return score_sheet.get_values()

def read_quiz():
    data = quiz_sheet.get_all_records(numericise_ignore=[2])
    return [{"id": row["id"], "question":row["question"], "answer":row["answer"] == 1} for row in data]


def write_score(data: dict, correct_ans: bool) -> float:
    if client_id == None:
        raise RuntimeError("%s.init() must be run before write." % __name__)

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

def write_quiz(quizzes: list[dict]):
    ids = []
    values = []

    for quiz in quizzes:
        if quiz["id"] not in ids:
            values.append([quiz["id"], quiz["question"], 1 if quiz["answer"] else 0])
            ids.append(quiz["id"])

    rows_count = len(ids)+1
    quiz_range = "A2:C%d" % (rows_count)

    quiz_sheet.resize(rows=rows_count, cols=3)
    quiz_sheet.batch_update([{"range": quiz_range, "values": values}])

    return ids
