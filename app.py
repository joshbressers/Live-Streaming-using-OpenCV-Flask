from flask import Flask, render_template, Response, redirect

from obj_detc import OpenCVHandler
from obj_detc import OpenCVColor
from obj_detc import AprilTagHandler

old_h = 0
old_s = 0
old_v = 0

app = Flask(__name__)

app.open_cv = OpenCVHandler()
app.cv_color = OpenCVColor(app.open_cv)
app.apriltag = AprilTagHandler(app.open_cv)

def gen_hsv(app):  # generate frame by frame from camera

    global old_h
    global old_s
    global old_v

    while True:
        # Capture frame-by-frame
        app.open_cv.update()

        height = app.open_cv.get_height()
        width = app.open_cv.get_width()

        x = int(width/2)
        y = int(height/2)

        hsv = app.open_cv.get_hsv()
        h, s, v = hsv[x][y]

        old_h = ((old_h * 99) + h) / 100
        old_s = ((old_s * 99) + s) / 100
        old_v = ((old_v * 99) + v) / 100

        app.open_cv.add_line((x-50,y), (x+50, y), [255, 0, 0])
        app.open_cv.add_line((x,y-50), (x, y+50), [255, 0, 0])

        app.open_cv.flip()

        app.open_cv.add_text((10, 25), "H: %d" % old_h)
        app.open_cv.add_text((10, 50), "S: %d" % old_s)
        app.open_cv.add_text((10, 75), "V: %d" % old_v)

        frame = app.open_cv.get_jpg_bytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

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

@app.route('/show_hsv')
def show_hsv():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_hsv(app), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/picker')
def picker():
    """Video streaming home page."""
    return render_template('picker.html')

@app.route('/see_hsv')
def see_hsv():
    """Video streaming home page."""
    return render_template('see_hsv.html')

@app.route("/set_color")
def do_set():
    app.cv_color.set()

    return redirect("/")


if __name__ == '__main__':

    #app.run(threaded=False)
    app.run()
