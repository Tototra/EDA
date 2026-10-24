import numpy as np
from flask import Flask, jsonify, request
from donnees import load, load_patterns, name
from affiches import posters, clean_title
from boucle import scores, first_round, draw, recommend, play, found_round
from personas import PERSONAS, favorites, liked_patterns

D, movies, users = load()
patterns, _ = load_patterns(movies)
sets = [set(F) for F in patterns]
fans = D.sum(axis=0)
titles = {movies.title[j] for F in patterns for j in F}
titles |= {movies.title[j] for w in PERSONAS.values() for j in favorites(w, movies)}
posters(sorted(titles))
rng = np.random.default_rng()
state = {}
app = Flask(__name__, static_folder="web", static_url_path="")


def cards(F):
    F = sorted(F, key=lambda j: -fans[j])
    urls = posters([movies.title[j] for j in F])
    result = []
    for j in F:
        title, year = clean_title(movies.title[j])
        result.append({"title": title, "year": year, "poster": urls[movies.title[j]]})
    return result


def describe(i):
    return {"id": int(i), "name": name(patterns[i], movies), "films": cards(patterns[i])}


def payload(chosen):
    return jsonify({"proposals": [describe(i) for i in chosen], "liked": len(state["liked"])})


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/wall")
def wall():
    urls = posters([movies.title[j] for j in np.argsort(-fans)[:60]])
    return jsonify([u for u in urls.values() if u])


@app.post("/api/start")
def start():
    state["likes"] = np.zeros(D.shape[1])
    state["dislikes"] = np.zeros(D.shape[1])
    state["shown"] = []
    state["liked"] = []
    return payload(first_round(sets, state["shown"], int(request.json["settings"]["k"]), rng))


@app.post("/api/feedback")
def feedback():
    for i in request.json["liked"]:
        state["likes"][patterns[int(i)]] += 1
        state["liked"].append(int(i))
    for i in request.json["passed"]:
        state["dislikes"][patterns[int(i)]] += 1
    settings = request.json["settings"]
    s = scores(patterns, state["likes"], state["dislikes"])
    return payload(draw(s, sets, state["shown"], float(settings["alpha"]), int(settings["k"]), rng))


@app.post("/api/best")
def best():
    s = scores(patterns, state["likes"], state["dislikes"])
    return jsonify([describe(i) for i in recommend(s, sets)])


@app.get("/api/personas")
def personas():
    return jsonify([{"id": n, "name": p, "films": cards(favorites(w, movies))} for n, (p, w) in enumerate(PERSONAS.items())])


@app.post("/api/persona/<int:n>")
def persona(n):
    liked = liked_patterns(list(PERSONAS.values())[n], movies, patterns)
    history = play(patterns, liked, D.shape[1], rng)
    last = found_round(history, liked) or len(history)
    rounds = []
    for t in range(last):
        before = history[t - 1][1] if t > 0 else []
        rounds.append([dict(describe(i), liked=bool(liked[i])) for i in history[t][1][len(before):]])
    return jsonify({"rounds": rounds, "best": [describe(i) for i in recommend(history[last - 1][0], sets)]})


if __name__ == "__main__":
    app.run(port=8000)
