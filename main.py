import os
import random
import string
from flask import Flask, flash, redirect, request, url_for
from flask import render_template
from models import db, URL

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

app.secret_key = os.urandom(24)  # For flash messages and sessions

# Configure the database URI and SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "urls.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app) # Initialize the db with the Flask App

# Create the database tables if they do not exist
with app.app_context():
    db.create_all()


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def is_valid_url(url):
    if not url.startswith(("http://", "https://")):
        return False
    return True


@app.route("/url_shortener", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form["long_url"]
        custom_code = request.form.get("custom_code", "").strip()

        if not is_valid_url(long_url):
            flash("Invalid URL. Please include 'http://' or 'https://'.", "error")
            return redirect(url_for("index"))

        short_code = custom_code if custom_code else generate_short_code()

        try:
            new_url = URL(short_code=short_code, long_url=long_url)
            # import ipdb;ipdb.set_trace()
            db.session.add(new_url)
            db.session.commit()
            shortened_url = url_for("redirect_url", code=short_code, _external=True)
            return render_template("shortened_url.html", shortened_url=shortened_url)
        except Exception as e:
            db.session.rollback() # rollback session on errors
            flash(
                "Custom short code is already taken. Please try another one.", "error"
            )
            return redirect(url_for("index"))
    return render_template("form_url_short.html")


@app.route("/<string:code>")
def redirect_url(code):
    url_data = URL.query.filter_by(short_code=code).first()
    if url_data:
        return redirect(url_data.long_url)
    else:
        return render_template("short_url_not_found.html"), 404




# uncomment this if deploying on aws
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=80)


# @app.route('/hello/')
# @app.route('/hello/<name>')
# def hello(name=None):
#     return render_template('hello.html', person=name)