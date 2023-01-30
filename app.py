from flask import Flask, render_template, Response, redirect
import cv2
import numpy as np
from statistics import mean

from obj_detc import OpenCVHandler
from obj_detc import OpenCVColor
from obj_detc import AprilTagHandler

app = Flask(__name__)

app.open_cv = OpenCVHandler()
app.cv_color = OpenCVColor(app.open_cv)
app.apriltag = AprilTagHandler(app.open_cv)

def c_picker(app):  # generate frame by frame from camera

    while True:
        # Capture frame-by-frame
        app.open_cv.update()
        frame = app.open_cv.get_frame(flipped=True)  # read the camera frame

        hsv = app.open_cv.get_hsv()

        height = app.open_cv.get_height()
        width = app.open_cv.get_width()

        # Let's draw a rectangle that's 100x100 in the middle of the screen
        w = 100
        h = 100

        x = int(width/2) - 50
        y = int(height/2) - 50

        cv2.rectangle(frame,(x,y),(x+w,y+h),[255,0,0],2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

# This function gets called by the /video_feed route below
def gen_frames(app):  # generate frame by frame from camera

    # We want to loop this forever
    while True:

        # Capture frame-by-frame
        app.open_cv.update()

        frame = app.cv_color.get_rectangle()

        # This step encodes the data into a jpeg image
        ret, buffer = cv2.imencode('.jpg', frame)

        # We have to return bytes to the user
        frame = buffer.tobytes()

        # Return the image to the browser
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(app), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/color_picker')
def color_picker():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(c_picker(app), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/picker')
def picker():
    """Video streaming home page."""
    return render_template('picker.html')

@app.route("/set_color")
def do_set():
    app.cv_color.set()

    return redirect("/")


if __name__ == '__main__':

    #app.run(threaded=False)
    app.run()
