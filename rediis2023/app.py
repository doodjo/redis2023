from flask import Flask, render_template, request, flash, redirect, url_for, json
import redis
import datetime
from collections import defaultdict

habits = ["Test habit"]
completions = defaultdict(list)

import redis

app = Flask(__name__)
app.secret_key = 'key'


r = redis.Redis('192.168.99.100')

last_id = 0

def scan_keys(pattern, pos: int = 0) -> list:
    gradovi = []
    while True:
        pos, val = r.scan(cursor=pos, match=pattern)
        gradovi = gradovi + val
        if pos == 0:
            break

    return gradovi

gradovi = scan_keys("grad Numero:*")
# print(gradovi)

######################################################################################## forum forma

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        global last_id #Misli se na ref na globalnu promenljivu
        req = request.form
        name = req["full_name"]
        post = req["data"]
        #print(name, post)

        last = r.get("last_id")
        #print("last_id", last)
        if last is None:
            last_id = 1
        else:
            last_id = int(last) #Mora da se kastuje u int zato sto redis sve cuva u byte-formi
            last_id += 1
        r.set(f"news:name:{last_id}", name) 
        r.set(f"news:post:{last_id}", post)
        r.set("last_id", last_id)
        r.lpush("post_id", last_id)
        flash("Objava uspešna, pogledajte 'Forum' ili 'Latest'!", category='success')

    return render_template("home.html")


######################################################################################## sub forma (ovo ne radi)


@app.route("/", methods=["GET", "POST"])
def add_sub(r: redis.Redis, itemid) -> None:
    pipe = r.pipeline()
    vrednosti = []
    
    if request.method == 'POST':
        if request.form.get('action1') == 'LIKES':
            pipe.hincrby(itemid, "nLikes", 1)
            pipe.append(vrednosti)
            pipe.execute()
        elif  request.form.get('action1') == 'LIKEP':
            pipe.hincrby(itemid, "nLikes", 1)
            pipe.append(vrednosti)
            pipe.execute()
        elif  request.form.get('action1') == 'LIKEM':
            pipe.hincrby(itemid, "nLikes", 1)
            pipe.append(vrednosti)
            pipe.execute()
        elif  request.form.get('action1') == 'LIKEK':
            pipe.hincrby(itemid, "nLikes", 1)
            pipe.append(vrednosti)
            pipe.execute()
        else:
            return None
    elif request.method == 'GET':
        return render_template('/likes', form=vrednosti)


######################################################################################## likes (ovo ne radi)

def scan(pattern, pos: int = 0) -> list:
    gradovi=[]
    while True:
        pos, val = r.scan(cursor=pos, match=pattern)
        gradovi = gradovi+val
        if pos == 0:
            break

    return gradovi
gradovi = scan_keys("grad:*")
print(gradovi)

# def likeCITY(r:redis.Redis. itemid) -> None:
#     nleft: bytes = r.hget(itemid, "nLikes")




######################################################################################## all

@app.route("/all")
def all_posts():
    post_ids = r.lrange("post_id", 0, -1)
    posts = dict()

    for post_id in post_ids:
        name = r.get(f'news:name:{post_id.decode("utf-8")}').decode("utf-8")
        post_data = r.get(f'news:post:{post_id.decode("utf-8")}').decode("utf-8")
        posts[name] = post_data

    return render_template("all.html", posts=posts)


######################################################################################## latest

@app.route("/latest")
def latest_posts():
    post_ids = r.lrange("post_id", 0, 2)
    posts = dict()

    for post_id in post_ids:
        name = r.get(f'news:name:{post_id.decode("utf-8")}').decode("utf-8")
        post_data = r.get(f'news:post:{post_id.decode("utf-8")}').decode("utf-8")
        posts[name] = post_data

    return render_template("latest.html", posts=posts)



######################################################################################## todo

@app.context_processor
def add_calc_date_range():
    def date_range(start: datetime.date):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates

    return {"date_range": date_range}


@app.route("/todo")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.date.fromisoformat(date_str)
    else:
        selected_date = datetime.date.today()

    return render_template(
        "todo.html",
        habits=habits,
        selected_date=selected_date,
        completions=completions[selected_date],
        title="ToDo - Home",
    )


@app.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    date = datetime.date.fromisoformat(date_string)
    habit = request.form.get("habitName")
    completions[date].append(habit)

    return redirect(url_for("todo.html", date=date_string))


@app.route("/add_habit", methods=["GET", "POST"])
def add_habit():
    if request.form:
        habits.append(request.form.get("habit"))

    return render_template(
        "add_habit.html",
        title="ToDo - Add",
        selected_date=datetime.date.today(),
    )


######################################################################################## logger


@app.route("/logger", methods=["GET", "POST", "DEL"])
def logger():
    return render_template("logger.html")


@app.route("/add-marker", methods=['POST'])
def add_marker():
    req = request.form
    location = req["lname"]
    latitude = req["latitude"]
    longitude = req["longitude"]

    print(location, latitude, longitude)

    

    r.geoadd("points", [longitude, latitude, location]) #Koriscenje geo 
    r.set("last_loc_name", location) #pamcenje zadnje lokacije u geo-spatial

    return redirect("/logger")

@app.route("/del-marker", methods=["GET", "POST", "DEL"])
def remove_marker():


    vrednost = r.get(name="last_loc_name")
    r.delete("last_loc_name")

    print(vrednost)
    return redirect("/logger")

@app.route("/data")
def geodata():
    lokacija___naziv = r.get("last_loc_name")
    lokacija__primitive = r.get("last_loc_name")

    if lokacija___naziv is None:
# Ovo postavljam zato sto mi treba jedno default mesto na koje ce google mapica da pokaze iako nema ni jedne dodate lokacije u db-u (ako uradim flushdb() ... npr)
        r.geoadd("points", ["-34.921230", "138.599503", "Adelejd"]) # ako nemam ni jednu lokaciju u bazi dodaje mi se ova lokacija kao default
        lokacija___naziv = "Adelejd"

# Sta prosledjujemo / naziv default lokacije / od te default lokacije koliko je maksimalna razdaljina sledece lokacije koja moze
# biti zadana (prosledio precnik Zemlje da ne bi mogli da crash-uju app)
    all___locations = r.georadiusbymember(name="points", member=lokacija___naziv, radius=4000, unit='mi', withcoord=True)
    print(all___locations)

    coordinates = dict()

    for loc in all___locations:
        city__name = loc[0].decode("utf-8")
        city__latitude = loc[1][1]
        city__longitude = loc[1][0]

        coordinates[city__name] = {"lat": city__latitude, "lng": city__longitude}

    return json.dumps(coordinates)

# Vraca poslednju dodatu lokaciju
@app.route("/last")
def last_loc():
    return r.get("last_loc_name").decode("utf-8")










# pokretanje

if __name__ == "__main__":
    app.run()

