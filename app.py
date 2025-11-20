from flask import Flask,render_template,request
import requests
import sqlite3

app=Flask(__name__)

API_KEY="5d559be809086ce1d35e611f3e09887f"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric"

def get_weather(city):
    url=BASE_URL.format(city,API_KEY)
    response=requests.get(url)
    if response.status_code==200:
        data=response.json()
        weather={
            "city":data["name"],
            "temperature":data["main"]["temp"],
            "humidity":data["main"]["humidity"],
            "description": data["weather"][0]["description"].capitalize(),
            "icon": data["weather"][0]["icon"]
        }
        return weather
    else:
        return None
    
def init_db():
    conn=sqlite3.connect("weather.db")
    c=conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              city TEXT,
              temperature REAL,
              description TEXT
              )''')
    
    conn.commit()
    conn.close()

def add_to_history(city,temp,desc):
    conn=sqlite3.connect("weather.db")
    c=conn.cursor()
    c.execute("INSERT INTO history (city,temperature,description) VALUES (?, ?, ?)",(city,temp,desc))
    conn.commit()
    conn.close()

def get_history():
    conn=sqlite3.connect("weather.db")
    c=conn.cursor()
    c.execute("SELECT city,temperature,description FROM history ORDER BY id DESC LIMIT 5")
    data=c.fetchall()
    conn.close()
    return data

@app.route("/", methods=["GET", "POST"])
def index():
    weather=None
    if request.method=="POST":
        city=request.form["city"]
        weather=get_weather(city)
        if weather:
            add_to_history(weather["city"],weather["temperature"],weather["description"])

    history=get_history()
    return render_template("index.html",weather=weather,history=history)

if __name__=="__main__":
    init_db()
    app.run(debug=True)