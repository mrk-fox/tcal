#This is the main file for the tcal software. 

# Elements: 1. Frontend - blessing, Middleend - Google API, Backend - Google

from blessed import Terminal
import os.path
import datetime as dt
import calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


term = Terminal()
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
SECRET = r"C:\Users\schar\Desktop_data\Documentation\client_secret_663060188113-93fagvpm0s53kvtt6mc889hlvvhqrhsc.apps.googleusercontent.com.json" #here the secret JSON file
BOXCHAR_L = ['│', '─', '┌', '┐', '└', '┘']
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MONTH_NAMES_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
S_NAME = "tcal v0.1"

now = dt.datetime.now()

month_view = 0
year_view = 0
day_select = 0
csy = 0
csx = 0
c_day = now.day
c_month =  now.month
c_year = now.year
cal_tbl = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0]
]


def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SECRET, SCOPES)
            creds = flow.run_local_server(port=0) #browser call
            with open("token.json", "w") as f:
                f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

service = get_service()

now = dt.datetime.now(dt.timezone.utc).isoformat()
events = service.events().list(
    calendarId="primary", timeMin=now, maxResults=20, singleEvents=True, orderBy="startTime").execute().get("items", [])

for e in events:
    start = e["start"].get("dateTime", e["start"].get("date"))
    print(start, e.get("summary", "(no title)"))

# the for loop is an example for a certain query.

# build the GUI

def draw_box(x, y, w, h):
    out = [term.move_xy(x, y) + BOXCHAR_L[2] + S_NAME + BOXCHAR_L[1]*(w - 2 - len(S_NAME)) + BOXCHAR_L[3]]
    for row in range(1, h-1):
        out.append(term.move_xy(x, y+row) + BOXCHAR_L[0] + " "* (w - 2) + BOXCHAR_L[0])
    out.append(term.move_xy(x, y+row) + BOXCHAR_L[4] + BOXCHAR_L[1]* (w - 2) + BOXCHAR_L[5])
    return "".join(out)

# («») - General width - 7*2+7
def draw_calendar(x, y, yr, m, d, csx, csy):
    global cal_tbl
    highlight_yr = False
    highlight_m = False
    if csy == 0:
        highlight_yr = True
        out = [term.move_xy(x, y) + " "*8 + term.black_on_yellow(str(yr)) + " "*7]
    else: 
        highlight_yr = False
        out = [term.move_xy(x, y) + " "*8 + str(yr) + " "*7]

    if csy == 1:
        highlight_m = True
        out.append(term.move_xy(x, y+1) + " "*8 + term.black_on_yellow(MONTH_NAMES_SHORT[m]) + " "*7)
    else:
        highlight_m = False
        out.append(term.move_xy(x, y+1) + " "*8 + MONTH_NAMES_SHORT[m] + " "*7)

    out.append(term.move_xy(x, y+2) + "M  T  W  T  F  S  S  ")
    first_wd = dt.date(yr, m, 1).weekday()

    i = 0 - first_wd
    line = 3
    for tx in range(5):
        out.append(term.move_xy(x, y+line))
        line += 1
        for ty in range(7):
            i += 1

            if i <= 0:
                cal_tbl[tx][ty] = i + days_in_month(yr, m-1)
            else:
                cal_tbl[tx][ty] = i
            
            if date_selected(tx, ty, i):
                out.append(term.black_on_yellow(str(cal_tbl[tx][ty])) + " "*(3-len(str(cal_tbl[tx][ty]))))
            else:
                out.append(str(cal_tbl[tx][ty]) + " "*(3-len(str(cal_tbl[tx][ty]))))

    return "".join(out)

def date_selected(x, y, i):
    global csx, csy
    if y == csx and x == csy:
        return True

def days_in_month(year, month):
    return calendar.monthrange(year, month)[1]

def read_keyinput():
    global csx, csy
    key = term.inkey(timeout=0.05)   # doubles as your frame delay
    if key.code == term.KEY_UP:
        csy -= 1
    elif key.code == term.KEY_DOWN:
        csy += 1        # 0 = year, 1 = month (raise as you add rows)
    elif key.code == term.KEY_LEFT:
        csx -= 1
    elif key.code == term.KEY_RIGHT:
        csx += 1
    return key



with term.fullscreen(), term.hidden_cursor(), term.cbreak():
    s_day = c_day
    s_month = c_month
    s_year = c_year
    while True:
        keyl = read_keyinput()

        out = draw_box(0, 0, term.width, term.height)
        out += draw_calendar(5, 5, s_day, s_month, s_year, csx, csy)

        print(out, end="", flush=True)        