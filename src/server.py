import json, time, math, tobii_research as tr
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

__DEBUG__ = 1
__PRETTY_DATA__ = 1

#### Helper Functions and Global Vars ####

# Server object
app = Flask(__name__)
# Solve CORS
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Data
OUTPUT = "data.json"
'''
Recorded from eyetracker
In format of:
LeftX  LeftY   RightX RightY Time_stamp
lx1     ly1     rx1     ry1      t1
lx2     ly2     rx2     ry2      t2
.        .       .       .        .
.        .       .       .        .
.        .       .       .        .

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
    time_stamp = float("%.5f"%tr.get_system_time_stamp())
    data = {"leftX": left[0], "leftY": left[1], "rightX": right[0], "rightY": right[1], "time": time_stamp}
    flag = 1
    if __PRETTY_DATA__:
        for v in data.values():
            flag &= not math.isnan(v)
    if flag:
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

def response(code, data=None):
    return jsonify({'code': code, 'data': data})

#### Helper Functions and Global Vars ####


#### Apis ####

'''
find and connect to eyetracker
'''
@app.route('/connect', methods=['POST', 'GET'])
@cross_origin()
def connectEyeTracker():
    global eyetracker
    found_eyetrackers = tr.find_all_eyetrackers()
    if len(found_eyetrackers) > 0:
        eyetracker = found_eyetrackers[0]
    code = None
    if eyetracker:
        code = SUCCESS_CODE
        debug("Connect to eyetracker successfully")
        return response(code, True)
    else:
        code = EYE_TRACKER_NOT_FOUND_CODE
        debug("Fail to connect to eyetracker")
        return response(code, False)
    

'''
disconnect to eyetracker (and unsubscribe from it if necessary)
'''
@app.route('/disconnect', methods=['POST', 'GET'])
@cross_origin()
def disconnectEyeTracker():
    global eyetracker
    unsubscribe()
    debug("Disconnect from eyetracker")
    eyetracker = None
    return response(SUCCESS_CODE, True)
'''
subscribe to eyetracker data, i.e., start recording
'''
@app.route('/subscribe', methods=['POST', 'GET'])
@cross_origin()
def subscribe():
    if not eyetracker:
        debug("No eyetracker found/connected")
        return response(EYE_TRACKER_NOT_FOUND_CODE, False)
    debug("Subscribe to eyetracker successfully")
    eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    return response(SUCCESS_CODE, True)

'''
subscribe to eyetracker data, i.e., start recording
'''
@app.route('/unsubscribe', methods=['POST', 'GET'])
@cross_origin()
def unsubscribe():
    debug("Unsubscribe from eyetracker successfully")
    if eyetracker:
        eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    return response(SUCCESS_CODE, True)
'''
Clear data
'''
@app.route('/clear', methods=['POST', 'GET'])
@cross_origin()
def clear():
    global Eye_Tracker_Data, Event_Data
    Eye_Tracker_Data = []
    Event_Data = []
    debug("Clear recorded data: Eye_Tracker_Data = %s, Event_Data = %s"%(
        str(Eye_Tracker_Data),
        str(Event_Data)
        ))
    return response(SUCCESS_CODE, True)

'''
Dump data
'''
@app.route('/dump', methods=['POST', 'GET'])
@cross_origin()
def dump():
    unsubscribe()
    debug("Dump to %s"%(OUTPUT))

    data = {"gazeData": Eye_Tracker_Data, "eventData": Event_Data}
    
    with open(OUTPUT, 'w') as f:
        json.dump(data, f)

    return response(SUCCESS_CODE, data)

'''
mark time stamps
'''
@app.route('/mark', methods=['POST', 'GET'])
@cross_origin()
def mark():
    time_stamp = "%.5f"%tr.get_system_time_stamp()
    global Eye_Tracker_Data, Event_Data

    if not eyetracker:
        debug("No eyetracker found")
        return response(EYE_TRACKER_NOT_FOUND_CODE, False)

    event_type = request.get_data()
    debug("Mark! Event: %s, Time_stamp: %s"%(event_type, time_stamp))

    data = {'type': event_type, 'time': time_stamp}
    Event_Data.append(data)
    return response(SUCCESS_CODE, data)


if __name__ == '__main__':
    app.run()

