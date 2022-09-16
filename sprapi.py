import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime
import os.path

path=os.path.dirname(os.path.abspath(__file__))

#Google Drive API
scope =['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(path+'/sodium-hue-361405-237068a500a2.json', scope)
client = gspread.authorize(creds)
s_sheet = client.open("MVP")
sheet1 = s_sheet.get_worksheet(0)
sheet2 = s_sheet.get_worksheet(1)

print("シート%d %d行%d列"%(sheet1.index,sheet1.row_count,sheet1.col_count))
print("シート%d %d行%d列"%(sheet2.index,sheet2.row_count,sheet2.col_count))

def load_ques():
    return sheet2.get_all_cells()

def load_ans():
    return sheet1.get_all_cells()

def write_ans(data,client_id:int,correct_ans:bool):
    answers=list(data.values())
    correct=answers.count(correct_ans)
    sum=len(answers)

    cells = sheet1.range(1, client_id, 4, client_id)
    cells[0].value = datetime.now().isoformat()
    cells[1].value = correct
    cells[2].value = sum
    cells[3].value = correct/sum

    sheet1.update_cells(cells)

with open(path+"/ans.json") as f:
    data=json.load(f)
    write_ans(data,1,False)