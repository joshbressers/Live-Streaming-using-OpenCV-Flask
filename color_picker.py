from flask import Flask, render_template, Response
import cv2
import numpy as np
from statistics import mean

app = Flask(__name__)

camera = cv2.VideoCapture(0)
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame

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

        print("Low: ", low, end='')
        print(" High:", high, end='')
        print(" Average: [%d, %d, %d]" % (int(mean(h)), int(mean(s)), int(mean(v))))

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
