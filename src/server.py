import json, time, tobii_research as tr
from flask import Flask, request

__DEBUG__ = 1

#### Helper Functions and Global Vars ####

# Server object
app = Flask(__name__)

# Data
EYE_TRACKER_DATA_FILE = "gazeData.txt"
EVENT_DATA_FILE = "eventData.txt"
'''
Recorded from eyetracker
In format of:
Left Right Time_stamp
l1    r1      t1
l2    r2      t2
.     .       .
.     .       .
.     .       .

'''
Eye_Tracker_Data = []

'''
Record event and its time
In format of:
Event Time_stamp
e1    t1
e2    t2
.     .
.     .
.     .

'''
Event_Data = []

# Data callback
def gaze_data_callback(gaze_data):
    global Eye_Tracker_Data
    left = gaze_data['left_gaze_point_on_display_area']
    right = gaze_data['right_gaze_point_on_display_area']
    time_stamp = float("%.20f"%time.time())
    data = [left, right, time_stamp]
    Eye_Tracker_Data.append(data)

# Eyetracker object
eyetracker = None

# Codes
SUCCESS_CODE = 200
EYE_TRACKER_NOT_FOUND_CODE = 404

# Error messages
EYE_TRACKER_NOT_FOUND_MESSAGE = "No eyetracker is found/connected."

# Helper
def debug(msg):
    if __DEBUG__:
        print msg

def response(code, message=None):
    return str({'code': code, 'message': message})

#### Helper Functions and Global Vars ####


#### Apis ####

'''
find and connect to eyetracker
'''
@app.route('/connect', methods=['POST'])
def connectEyeTracker():
    global eyetracker
    found_eyetrackers = tr.find_all_eyetrackers()
    if len(found_eyetrackers) > 0:
        eyetracker = found_eyetrackers[0]
    code = None
    msg = None
    if eyetracker:
        code = SUCCESS_CODE
        debug("Connect to eyetracker successfully")
    else:
        code = EYE_TRACKER_NOT_FOUND_CODE
        debug("Fail to connect to eyetracker")
    return response(code, msg)

'''
disconnect to eyetracker (and unsubscribe from it if necessary)
'''
@app.route('/disconnect', methods=['POST'])
def disconnectEyeTracker():
    global eyetracker
    unsubscribe()
    debug("Disconnect from eyetracker")
    eyetracker = None
    return response(SUCCESS_CODE)
'''
subscribe to eyetracker data, i.e., start recording
'''
@app.route('/subscribe', methods=['POST'])
def subscribe():
    if not eyetracker:
        debug("No eyetracker found/connected")
        return response(EYE_TRACKER_NOT_FOUND_CODE, EYE_TRACKER_NOT_FOUND_MESSAGE)
    debug("Subscribe to eyetracker successfully")
    eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    return response(SUCCESS_CODE)

'''
subscribe to eyetracker data, i.e., start recording
'''
@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    debug("Unsubscribe from eyetracker successfully")
    if eyetracker:
        eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    return response(SUCCESS_CODE)
'''
Clear data
'''
@app.route('/clear', methods=['POST'])
def clear():
    global Eye_Tracker_Data, Event_Data
    Eye_Tracker_Data = []
    Event_Data = []
    debug("Clear recorded data: Eye_Tracker_Data = %s, Event_Data = %s"%(
        str(Eye_Tracker_Data),
        str(Event_Data)
        ))
    return response(SUCCESS_CODE)

'''
Dump data
'''
@app.route('/dump', methods=['POST'])
def dump():
    debug("Dump to %s, %s"%(EYE_TRACKER_DATA_FILE, EVENT_DATA_FILE))
    with open(EYE_TRACKER_DATA_FILE, 'w') as f:
        for d in Eye_Tracker_Data:
            f.write(str(d) + "\r\n")
            
    with open(EVENT_DATA_FILE, 'w') as f:
        for d in Event_Data:
            f.write(str(d) + "\r\n")
    return response(SUCCESS_CODE)

'''
mark time stamps
'''
@app.route('/mark', methods=['POST'])
def mark():
    time_stamp = time.time()
    global Event_Data
    '''
    if not eyetracker:
        debug("No eyetracker found")
        return response(EYE_TRACKER_NOT_FOUND_CODE, EYE_TRACKER_NOT_FOUND_MESSAGE)
    '''
    event_type = request.get_data()
    debug("Mark! Event: %s, Time_stamp: %.20f"%(event_type, time_stamp))

    Event_Data.append([event_type, time_stamp])
    return response(SUCCESS_CODE)


if __name__ == '__main__':
    app.run()

