import time, tobii_research as tr

my_eyetracker = tr.find_all_eyetrackers()[0]

print("Address: " + my_eyetracker.address)
print("Name (It's OK if this is empty): " + my_eyetracker.device_name)


def gaze_data_callback(gaze_data):
    # Print gaze points of left and right eye
    #print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
    #    gaze_left_eye=gaze_data['left_gaze_point_on_display_area'],
    #    gaze_right_eye=gaze_data['right_gaze_point_on_display_area']))
    print "python_returned: %s \t computer_system: %s \t tobii_device: %s"%(time.time(), gaze_data['system_time_stamp'], gaze_data['device_time_stamp'])

my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

time.sleep(1)

my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
