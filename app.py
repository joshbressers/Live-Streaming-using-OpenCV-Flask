from flask import Flask, render_template, Response
import cv2
import numpy as np

app = Flask(__name__)

camera = cv2.VideoCapture(0)
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Red
        #lower_color = np.array([100,100,70], dtype=np.uint8)
        #upper_color = np.array([220,255,255], dtype=np.uint8)

        # Blue
        lower_color = np.array([100,100,100], dtype=np.uint8)
        upper_color = np.array([110,130,150], dtype=np.uint8)

        # Threshold the HSV image to get only blue colors
        mask = cv2.inRange(hsv, lower_color, upper_color)
        #cv2.imshow('mask',mask)
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(frame,frame, mask= mask)
        #cv2.imshow("b", res)

        imgray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,127,255,0)
        contours, hierarchy = cv2.findContours(imgray,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        rectangle = {
            "area": 0,
            "x": 0,
            "y": 0,
            "w": 0,
            "h": 0
        }

        for cnt in contours:
            x,y,w,h = cv2.boundingRect(cnt)

            if w * h > rectangle["area"]:
                rectangle["area"] = w * h
                rectangle["x"] = x
                rectangle["y"] = y
                rectangle["w"] = w
                rectangle["h"] = h

            #cx,cy = int(x+w/2), int(y+h/2)
            #if not (w < 20 or h < 20):
            #    cv2.rectangle(frame,(x,y),(x+w,y+h),[255,0,0],2)
                #if 100 < res.item(cy,cx,0) < 120:
                #    cv2.rectangle(frame,(x,y),(x+w,y+h),[255,0,0],2)

        # Only frame the biggest rectangle
        x = rectangle["x"]
        y = rectangle["y"]
        w = rectangle["w"]
        h = rectangle["h"]
        cv2.rectangle(frame,(x,y),(x+w,y+h),[255,0,0],2)

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
