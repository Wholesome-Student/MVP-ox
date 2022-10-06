import time
import random
import os.path

import gspread
import gspread.utils

# Directory where this python file is
path = os.path.dirname(os.path.abspath(__file__))


class MVPSpreadsheetAPIError(Exception):
    """Base exception class for MVP_Spreadsheet_API."""
    pass


class MVPPermissionError(MVPSpreadsheetAPIError):
    """Not enough permissions."""
    pass


class MVPAccessBase():
    def __init__(self) -> None:
        self._connect = False
        self._client_id = None
        self._ishost = False

    def read_state(self) -> dict[str, gspread.utils.numericise]:
        """Return state of MVP.
        
        Requests
        --------
        read requests: 1
        write requests: 0

        Returns
        -------
        state : dict[:class:`str`, :class:`Any`]
            state of MVP.
        """
        data = self._state_sheet.get_values()
        return {row[0]: gspread.utils.numericise(row[1]) for row in data if row[0]}

    def read_score(self) -> dict[int, list[gspread.utils.numericise]]:
        """Return score for each client.
        
        Requests
        --------
        read requests: 1
        write requests: 0

        Returns
        -------
        state : dict[:class:`int`, list[:class:`Any`]]
            dict of score for each client.
        """
        data = self._score_sheet.get_values()
        return {i+1: [gspread.utils.numericise(col) for col in row] for i,row in enumerate(data)}

    def read_quiz(self) -> list[dict]:
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
        data = self._quiz_sheet.get_all_records(numericise_ignore=[2])
        return [{"id": row["id"], "question":row["question"], "answer":row["answer"] == 1} for row in data]
    
    def read_client(self) -> dict[str, gspread.utils.numericise]:
        """Return clients state.
        
        Requests
        --------
        read requests: 1
        write requests: 0

        Returns
        -------
        state : dict[:class:`str`, :class:`Any`]
            state of clients.
        """
        data = self._init_sheet.get_values()
        return {i+1: gspread.utils.numericise(row[1]) for i,row in enumerate(data)}



class MVPClient(MVPAccessBase):
    """Client for MVP_Spreadsheet_API.
    
    Requests(init)
    --------
    read requests: 1
    write requests: 1

    Raises
    ------
    RuntimeError
        Server is not in initialization state.
    """
    def __init__(self) -> None:
        super().__init__()

        # Google Drive API
        self._client = gspread.service_account(filename=path+"/client1.json")
        self._spr = self._client.open("MVP")
        self._state_sheet = self._spr.worksheet("state")
        self._score_sheet = self._spr.worksheet("score")
        self._quiz_sheet = self._spr.worksheet("quiz")
        self._init_sheet = self._spr.worksheet("init")

        state = self.read_state()
        if state["state_code"] != 10:
            raise RuntimeError("server is not in initialization state.")
        rand = "%02x" % random.randint(0x0,0xff)
        response = self._init_sheet.append_row([rand,1],include_values_in_response=True)
        updatedData = response["updates"]["updatedData"]
        self._connect = True
        self._client_id = gspread.utils.a1_to_rowcol(updatedData["range"].split("!")[-1])[0]

    def close(self) -> None:
        if self._connect:
            self._init_sheet.update_cell(row=self._client_id, col=2, value=0)
            self._connect = False

    @property
    def client_id(self) -> int:
        """:class:`int`: ID assigned to this client."""
        return self._client_id

    def write_score(self, user_ans: dict[str, bool], correct_ans: bool) -> float:
        """Write number of correct answers, number of answers, and correct answer rate of this clients.
        Return correct answer rate of this clients.
        
        Requests
        --------
        read requests: 1
        write requests: 1

        Parameters
        ----------
        user_ans : dict[:class:`str`, :class:`bool`]
            Dict of answer for each user of this client.
        correct_ans : :class:`bool`
            Correct answer for this question.

        Returns
        -------
        rate : float
            Correct answer rate of this clients.
        """
        if not self._connect:
            raise MVPPermissionError("not connected")

        answers = list(user_ans.values())

        cells = self._score_sheet.range(self._client_id, 1, self._client_id, 4)

        correct = cells[1].numeric_value+answers.count(correct_ans)
        sum = cells[2].numeric_value+len(answers)
        rate = correct/sum

        cells[0].value = time.time()
        cells[1].value = correct
        cells[2].value = sum
        cells[3].value = rate

        self._score_sheet.update_cells(cells)

        return rate



class MVPHost(MVPAccessBase):
    """Host for MVP_Spreadsheet_API.
    This try to write state_code to 0 when the instance is about to be destroyed.
    
    Requests(init)
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
        Other host has connected to MVP.
    """
    def __init__(self,client_count: int) -> None:
        super().__init__()

        # Google Drive API
        self._client = gspread.service_account(filename=path+"/host.json")
        self._spr = self._client.open("MVP")
        self._state_sheet = self._spr.worksheet("state")
        self._score_sheet = self._spr.worksheet("score")
        self._quiz_sheet = self._spr.worksheet("quiz")
        self._init_sheet = self._spr.worksheet("init")

        if int(client_count) <= 0:
            raise ValueError("client_count must be >0.")
        state = self.read_state()
        if state["state_code"] != 0:
            raise RuntimeError("other server has connected.")
        self._connect = True
        self._ishost = True
        self._init_sheet.resize(rows=1, cols=2)
        self._init_sheet.clear()
        state["state_code"] = 10
        state["clients_count"] = int(client_count)
        self.write_state(state)

    def close(self) -> None:
        if self._connect:
            self.write_state({"state_code":0})
            self._connect = False

    def write_state(self, state: dict):
        if not self._connect:
            raise MVPPermissionError("not connected")
        values = [[key, state[key]] for key in state]
        state_range = "A1:B%d" % len(values)
        self._state_sheet.resize(rows=len(values), cols=3)
        self._state_sheet.batch_update([{"range": state_range, "values": values}])

    def write_quiz(self, quizzes: list[dict]) -> list:
        if not self._connect:
            raise MVPPermissionError("not connected")
        ids = []
        values = []

        for quiz in quizzes:
            if quiz["id"] not in ids:
                values.append([quiz["id"], quiz["question"], 1 if quiz["answer"] else 0])
                ids.append(quiz["id"])

        rows_count = len(ids)+1
        quiz_range = "A2:C%d" % (rows_count)

        self._quiz_sheet.resize(rows=rows_count, cols=3)
        self._quiz_sheet.batch_update([{"range": quiz_range, "values": values}])

        return ids
