from warnings import catch_warnings
from flask import Flask, redirect, url_for, render_template, send_file
from flask_wtf.file import FileField
from flask import request
from wtforms import SubmitField
from flask_wtf import Form
import sqlite3
from io import BytesIO
from fer import FER
import matplotlib.pyplot as plt
import tensorflow
from tensorflow import keras
import os
import cv2
import time
import matplotlib.pyplot as plot


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"


@app.route('/')
def capture():
    return render_template("main.html")


@app.route('/loadindex')
def loadindex():
    return render_template("index.html")


@app.route('/loadindex2', methods=["GET", "POST"])
def loadindex2():
    form = UploadForm()
    if request.method == "POST":
        if form.validate_on_submit():
            file_name = form.file.data
            database(name=file_name.filename, data=file_name.read())
            print("FILE : {}".format(file_name.filename))
            img = plt.imread(form.file.data)
            f = "graph" + str(time.time()) + ".png"

            for fn in os.listdir('static/'):
                # not to remove other images
                if fn.startswith('graph'):
                    os.remove('static/' + fn)

            cv2.imwrite(os.path.join('static', f), img)
            print("pic saved")
            detector = FER()
            res = (detector.detect_emotions(img))[-1]['emotions']
            print((detector.detect_emotions(img)))
            happy = res['happy']
            angry = res['angry']
            disgust = res['disgust']
            fear = res['fear']
            sad = res['sad']
            surprise = res['surprise']
            neutral = res['neutral']
            return render_template("index2.html", form=form, happy=happy, angry=angry, disgust=disgust, fear=fear, sad=sad, surprise=surprise, neutral=neutral, file_name=f)
    return render_template("index2.html", form=form)


class UploadForm(Form):
    file = FileField()
    submit = SubmitField("submit")
    download = SubmitField("download")


def database(name, data):
    conn = sqlite3.connect("COPY.db")
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS my_table(name TEXT, data BLOP)""")
    cursor.execute(
        """INSERT INTO my_table(name, data) VALUES (?,?)""", (name, data))

    conn.commit()
    cursor.close()
    conn.close()


@ app.route('/capture', methods=["GET", "POST"])
def index():
    cam = cv2.VideoCapture(0)

    cv2.namedWindow("test")

    img_counter = 0
    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            file_name = "graph" + str(time.time()) + ".png"

            for filename in os.listdir('static/'):
                # not to remove other images
                if filename.startswith('graph'):
                    os.remove('static/' + filename)

            cv2.imwrite(os.path.join('static', file_name), frame)
            print("pic saved")

            #cv2.imwrite(os.path.join('static', img_name), frame)
            #print(os.path.join('static', img_name))
            #img_path = os.path.join('static', img_name)
            detector = FER()
            res = []
            try:
                res = (detector.detect_emotions(frame))[-1]['emotions']
                print((detector.detect_emotions(frame)))
            except:
                cam.release()
                cv2.destroyAllWindows()
                return render_template("index.html", comment="Face not found")
            happy = res['happy']
            angry = res['angry']
            disgust = res['disgust']
            fear = res['fear']
            sad = res['sad']
            surprise = res['surprise']
            neutral = res['neutral']
            #print("{} written!".format(img_name))
            img_counter += 1
            cam.release()
            cv2.destroyAllWindows()
            return render_template("index.html", happy=happy, angry=angry, disgust=disgust, fear=fear, sad=sad, surprise=surprise, neutral=neutral, file_name=file_name)
    cam.release()
    cv2.destroyAllWindows()
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
