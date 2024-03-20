#graphs.py
import pandas as pd;

OE = "OddEven"
PT = "PublicTransport"
EV = "ElectricVehicle"
DATE = "Date"
BREAKTYPE = "Break"

PTnum = 0
OEnum = 0
EVnum = 0

date_lis = []
OE_breaks = []
PT_breaks = []
EV_breaks = []

#path_to_csv = getPath();
def readCSV(path_to_csv:str):
    dataset = pd.read_csv(path_to_csv)
    return dataset

# getters
def get_PT():
    return PT_breaks
def get_EV():
    return EV_breaks
def get_OE():
    return OE_breaks
def get_date_lis():
    return date_lis

def get_last_row(df_str):
    try:
        df = pd.read_csv(df_str)
        last_row = df.iloc[-1].tolist()
        add_last_row(last_row)
    except pd.errors.EmptyDataError:
        return None

def add_last_row(last_row):
    new_date = last_row[0]
    new_break = last_row[1]
    index = 0
    if new_date not in date_lis:
        date_lis.append(new_date)
        if new_break == OE:
            OE_breaks.append(1)
            PT_breaks.append(0)
            EV_breaks.append(0)
        elif new_break == PT:
            OE_breaks.append(0)
            PT_breaks.append(1)
            EV_breaks.append(0)
        elif new_break == EV:
            OE_breaks.append(0)
            PT_breaks.append(0)
            EV_breaks.append(1)
    else:
        for date in date_lis:
            if date == new_date:
                break
            index += 1
        if new_break == OE:
            OE_breaks[index] += 1
        elif new_break == PT:
            PT_breaks[index] += 1
        elif new_break == EV:
            EV_breaks[index] += 1

def date_to_list(df, dl):
    for d in df[DATE]:
        if d not in date_lis:
            dl.append(d)
    dl.sort()
    return dl

def add_all_data(df, dl):
    for d in dl:
        break_nums = set_breaks(df, d)
        PT_breaks.append(break_nums[0])
        OE_breaks.append(break_nums[1])
        EV_breaks.append(break_nums[2])

# def addBreak() add to csv
def set_breaks(df, d):
    filtered_df = df[df[DATE] == d]
    PTnum = 0
    OEnum = 0
    EVnum = 0

    for break_type in filtered_df[BREAKTYPE]:
        if break_type == PT:
            PTnum += 1
        elif break_type == OE:
            OEnum += 1
        elif break_type == EV:
            EVnum += 1
    if (PTnum == 0):
        PTnum = 0.001
    if (OEnum == 0):
        OEnum = 0.001
    if (EVnum == 0):
        EVnum = 0.001      
    return [PTnum, OEnum, EVnum]