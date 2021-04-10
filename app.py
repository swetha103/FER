from flask import Flask, redirect, url_for, render_template, send_file
from flask_wtf.file import FileField
from flask import request
from wtforms import SubmitField
from flask_wtf import Form
import sqlite3
from io import BytesIO
from fer import FER
import matplotlib.pyplot as plt


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"


@app.route('/', methods=["GET", "POST"])
def index():
    form = UploadForm()
    if request.method == "POST":
        if form.validate_on_submit():
            file_name = form.file.data
            database(name=file_name.filename, data=file_name.read())
            print("FILE : {}".format(file_name.filename))
            img = plt.imread(form.file.data)
            detector = FER(mtcnn=True)
            res = (detector.detect_emotions(img))[-1]['emotions']
            happy = res['happy']
            angry = res['angry']
            disgust = res['disgust']
            fear = res['fear']
            sad = res['sad']
            surprise = res['surprise']
            neutral = res['neutral']
            print(happy)
            plt.imshow(img)
            return render_template("home.html", form=form, happy=happy, angry=angry, disgust=disgust, fear=fear, sad=sad, surprise=surprise, neutral=neutral)
    return render_template("home.html", form=form)


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


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
