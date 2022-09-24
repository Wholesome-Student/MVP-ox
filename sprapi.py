from datetime import datetime
import random
import os.path

import gspread

# Directory where this python file is
path = os.path.dirname(os.path.abspath(__file__))

client_id = None  # 0:host 1-10:client
state = {"state_code": 0}

# Google Drive API
client = gspread.service_account(filename=path+"/sodium-hue-361405-237068a500a2.json")
spr = client.open("MVP")
state_sheet = spr.worksheet("state")
score_sheet = spr.worksheet("score")
quiz_sheet = spr.worksheet("quiz")
init_sheet = spr.worksheet("init")


class MVPSpreadsheetAPIError(Exception):
    """Base exception class for MVP_Spreadsheet_API."""
    pass

class MVPPermissionError(MVPSpreadsheetAPIError):
    """Not enough permissions."""
    pass

def client_init() -> int:
    """Get and return client_id.
    
    Requests
    --------
    read requests: 1
    write requests: 1

    Returns
    -------
    client_id : :class:`int`
        ID assigned to this client.

    Raises
    ------
    RuntimeError
        This client or host has connected.
    """
    global client_id
    if client_id != None:
        raise RuntimeError("init function can only be run once.")
    state = read_state()
    if state["state_id"] != 10:
        raise RuntimeError("server is not in initialization state.")
    rand = random.randint(0x0,0xff)
    response = init_sheet.append_row([rand],include_values_in_response=True)
    updatedData = response["updates"]["updatedData"]
    client_id = gspread.utils.a1_to_rowcol(updatedData["range"].split("!")[-1])[0]
    return client_id


def server_init(client_count: int):
    """Initialize and allow clients to connect.
    
    Requests
    --------
    read requests: 1
    write requests: 3

    Parameters
    ----------
    client_count : :class:`int`
        Number of clients to connect.

    Raises
    ------
    RuntimeError
        This client or host has connected.
    """
    global client_id
    if client_id != None:
        raise RuntimeError("init function can only be run once.")
    if int(client_count) <= 0:
        raise ValueError("client_count must be >0.")
    state = read_state()
    if state["state_id"] != 0:
        raise RuntimeError("other server has connected.")

    client_id = 0
    init_sheet.resize(rows=1, cols=2)
    init_sheet.clear()
    state["state_code"] = 10
    state["clients_count"] = int(client_count)
    state["clients_remaining"] = int(client_count)
    write_state(state)

def wait_client():
    if client_id != 0:
        raise MVPPermissionError("only host can run %s.wait_client()." % __name__)
    clients = init_sheet.get_values()
    # 未完成


def read_state() -> dict[str, str]:
    """Return state of MVP.
    
    Requests
    --------
    read requests: 1
    write requests: 0

    Returns
    -------
    state : dict[:class:`str`, :class:`str`]
        state of MVP.
    """
    data = state_sheet.get_values()
    return {row[0]: row[1] for row in data if row[0]}

def read_score() -> list[list]:
    """Return score for each client.
    
    Requests
    --------
    read requests: 1
    write requests: 0

    Returns
    -------
    state : list[:class:`list`]
        list of score for each client.
    """
    return score_sheet.get_values()

def read_quiz() -> list[dict]:
    """Return quiz list.
    
    Requests
    --------
    read requests: 1
    write requests: 0

    Returns
    -------
    state : list[:class:`dict`]
        list of quiz.
    """
    data = quiz_sheet.get_all_records(numericise_ignore=[2])
    return [{"id": row["id"], "question":row["question"], "answer":row["answer"] == 1} for row in data]


def write_state(state: dict):
    if client_id != 0:
        raise MVPPermissionError("only host can run %s.write_state()." % __name__)

    values = [[key, state[key]] for key in state]
    state_range = "A1:B%d" % len(values)
    state_sheet.resize(rows=len(values), cols=3)
    state_sheet.batch_update([{"range": state_range, "values": values}])

def write_score(user_ans: dict[str, bool], correct_ans: bool) -> float:
    """Write number of correct answers, number of answers, and correct answer rate of this clients.
    Return correct answer rate of this clients.
    
    Requests
    --------
    read requests: 1
    write requests: 1

    Parameters
    ----------
    user_ans : dict[:class:`str`, :class:`bool`]
        Dict of answer for each user of this client
    correct_ans : bool
        Correct answer for this question

    Returns
    -------
    rate : float
        Correct answer rate of this clients.

    Raises
    ------
    MVPPermissionError
        Client does not have client_id. (Run client_init() first.)
    """
    if client_id == None or client_id == 0:
        raise MVPPermissionError("%s.client_init() must be run before write score." % __name__)

    answers = list(user_ans.values())

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

    return len(ids)
