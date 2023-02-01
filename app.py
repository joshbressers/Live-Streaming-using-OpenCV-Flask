#!/usr/bin/env python

from threading import Thread
from flask import Flask, render_template, Response, redirect
import time

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

        height = app.open_cv.get_height()
        width = app.open_cv.get_width()

        x = int(width/2) - 50
        y = int(height/2) - 50

        app.open_cv.add_rectangle((x,y), (x+100, y+100), [255,0,0])
        frame = app.open_cv.get_jpg_bytes(flipped=True)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

# This function gets called by the /video_feed route below
def gen_frames(app):  # generate frame by frame from camera

    # We want to loop this forever
    while True:

        # Capture frame-by-frame
        app.open_cv.update()
        if app.apriltag.check():
            app.apriltag.add_rectangle()

        app.cv_color.add_rectangle()

        frame = app.open_cv.get_jpg_bytes()
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

    thread = Thread(target=app.run)
    thread.start()

    while True:
        # Do things in here
        time.sleep(1)
