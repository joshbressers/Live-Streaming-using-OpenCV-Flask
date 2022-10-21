from flask import Flask, render_template, Response, redirect
import cv2
import numpy as np
from statistics import mean

app = Flask(__name__)

# Capture the first camera on the system
camera = cv2.VideoCapture(0)

# Example Red
lower_color = np.array([150,100,100], dtype=np.uint8)
upper_color = np.array([220,255,255], dtype=np.uint8)

# Example Blue
#lower_color = np.array([100,100,100], dtype=np.uint8)
#upper_color = np.array([110,130,150], dtype=np.uint8)

average_color = np.array([255,255,255], dtype=np.uint8)

def c_picker():  # generate frame by frame from camera

    global average_color

    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break

        frame = cv2.flip(frame, 1)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        height = len(hsv)
        width = len(hsv[0])

        # Let's draw a rectangle that's 100x100 in the middle of the screen
        w = 100
        h = 100

        x = int(width/2) - 50
        y = int(height/2) - 50

        cv2.rectangle(frame,(x,y),(x+w,y+h),[255,0,0],2)

        # Now we want to find the high and low colors, then print them
        low = hsv[0][0]
        high = hsv[0][0]

        h = []
        s = []
        v = []

        for i in range(x, x + 100):
            for j in range(y, y + 100):

                h.append(hsv[j][i][0])
                s.append(hsv[j][i][1])
                v.append(hsv[j][i][2])

                if hsv[j][i][0] < low[0]:
                    low = hsv[j][i]
                if hsv[j][i][0] > high[0]:
                    high = hsv[j][i]

        average_color[0] = int(mean(h))
        average_color[1] = int(mean(s))
        average_color[2] = int(mean(v))

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

# This function gets called by the /video_feed route below
def gen_frames():  # generate frame by frame from camera

    global lower_color
    global upper_color

    # We want to loop this forever
    while True:

        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame

        # If something goes wrong with the camera, exit the function
        if not success:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_color, upper_color)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #bilateral_filtered_image = cv2.bilateralFilter(frame, 5, 175, 175)
        #edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)
        #contours, hierarchy = cv2.findContours(edge_detected_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #imgray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        #contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contour_list = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True),True)
            area = cv2.contourArea(contour)
            if ((len(approx) > 8) & (len(approx) < 23) & (area > 30) ):
                contour_list.append(contour)

        frame = cv2.drawContours(frame, contour_list, -1, (0,255,0), 3)

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
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/color_picker')
def color_picker():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(c_picker(), mimetype='multipart/x-mixed-replace; boundary=frame')


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
    global lower_color
    global upper_color
    global average_color

    h = average_color[0]
    s = average_color[1]
    v = average_color[2]

    hl = h - 50
    if hl < 0: hl = 0
    sl = s - 50
    if sl < 0: sl = 0
    vl = v - 50
    if vl < 0: vl = 0
    lower_color = np.array([hl,sl,vl], dtype=np.uint8)

    hh = h + 50
    if hh > 255: hl = 255
    sh = s + 50
    if sh > 255: sh = 255
    vh = v + 50
    if vh > 255: vh = 255
    upper_color = np.array([hh,sh,vh], dtype=np.uint8)

    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
