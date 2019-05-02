from flask import *
from flask_pymongo import PyMongo
import pymongo
from pymongo import MongoClient
import requests
import hashlib
import string

app = Flask(__name__)

app.secret_key = "secret"

client = MongoClient("mongodb://127.0.0.1:27017")
db = client["nyuit"]
userlist = db["users"]

categoryList = ["Arts & Theatre", "Film", "Miscellaneous", "Music", "Sports", "Undefined", "Donation", "Event Style", "Group", "Individual", "Merchandise", "Nonticket", "Parking", "Transportation", "Upsell", "Venue Based"]

genreId = {'R&B': 'KnvZfZ7vAee',
'Hip-Hop/Rap': 'KnvZfZ7vAv1',
'Comedy': 'KnvZfZ7vAe1',
'Classical': 'KnvZfZ7v7nJ',
'Jazz': 'KnvZfZ7vAvE',
'Foreign': 'KnvZfZ7vAk1',
'Dance': 'KnvZfZ7vAvF',
'Electronic': 'KnvZfZ7vAvF',
'Comedy': 'KnvZfZ7vAkA',
'Animation': 'KnvZfZ7vAkd',
'Music': 'KnvZfZ7vAkJ',
'Miscellaneous': 'KnvZfZ7vAka',
'Family': 'KnvZfZ7vAkF',
'Miscellaneous Theatre': 'KnvZfZ7v7ld',
'Theatre': 'KnvZfZ7v7l1'
}

@app.route("/")
def home():
    if 'username' not in session:
        return render_template("home.html")
    else:
        return render_template("home.html", username = session["username"])

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = hashlib.sha256((request.form['password']).encode("utf-8"))
        password = request.form['password']
        category = request.form['category']
        genre = request.form['genre']
        newUser = True
        for i in userlist.find({'username':username}):
            newUser = False
        if newUser:
            session['username'] = username
            userlist.insert({'username':username, 'password':password, 'category':category, 'genre':genre})
            return redirect("/")
        else:
            return render_template("register.html", message = "User already exists!")
    else:
        return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = hashlib.sha256((request.form['password']).encode("utf-8"))
        password = request.form['password']
        exist = False
        for i in userlist.find({'username':username}):
            exists = True
        if exists:
            passmatch = False
            for i in userlist.find({'username':username, 'password':password}):
                passmatch = True
            if passmatch:
                session['username'] = username
                return redirect("/")
            else:
                return render_template('login.html', message = "Username and Password don't match")
        else:
            # Have same error message promotes security
            return render_template('login.html', message = "Username and Password don't match")
    else:
        return render_template("login.html")

@app.route('/getEvents', methods=['GET', 'POST'])
def getEvents():
    if 'username' not in session:
        return render_template("home.html", message = "You must be logged in to do this")
    else:
        username = session['username']
        user = userlist.find_one({"username":username})
        category = user['category']
        genre = genreId[user['genre']]
        requestString = "https://yv1x0ke9cl.execute-api.us-east-1.amazonaws.com/prod/events"
        requestString += ("?classificationName="+category)
        requestString += ("&genreId="+genre)
        r = requests.get(requestString, auth=('stitapplicant','zvaaDsZHLNLFdUVZ_3cQKns'))
        print(r)
        print(r.content)
        return render_template("getEvents.html", message = r.content)

@app.route('/preferences', methods=['GET', 'POST'])
def setPreferences():
    if 'username' not in session:
        return render_template("home.html", message = "You must be logged in to view stats")
    else:
        if request.method == "POST":
            username = session['username']
            category = request.form['category']
            genre = request.form['genre']
            userlist.update({"username":username}, {"$set":{"category":category, "genre":genre}})
            return render_template("preferences.html", message = "success")
        else:
            return render_template("preferences.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/")


if __name__  == "__main__":
    app.run(debug=True)
