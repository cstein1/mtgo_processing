from flask import Flask, render_template, request, url_for, redirect, session

import mtg_helper

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

@app.route('/')
def index():
    return render_template('index.html')


def render_fail_case(error=None):
    print("Internal error of: " + error)
    return app.redirect(app.url_for(endpoint="draft_ingest_file", error=error), 400)

draft_key = "draft"
deck_key = "deck"
pick_key = "pick"
picked_url_key = "picked_url"
choice_result_key = "choice_result"

@app.route('/draft/play', methods=["POST", "GET"])
def draft_play():
    # File is draft! Time to play :)
    draft = mtg_helper.Draft(str(session[draft_key]))
    session[deck_key] = []
    session[pick_key] = 0
    session[picked_url_key] = []
    session[choice_result_key] = 0

    return render_template('game.html', draft=draft, pick=0)

@app.route('/draft/card/<card>', methods=["POST"])
def click_card(card: str):
    draft_instance = mtg_helper.Draft(session[draft_key])
    draft_list = draft_instance.to_list()
    session[deck_key].append(draft_list[session[pick_key]][draft_instance.PICK])

    if card == draft_list[session[pick_key]][draft_instance.PICK]:
        session[choice_result_key] += 1

    # Add a check for exceeding number here
    if int(session[pick_key]) >= len(draft_instance.packs)-1:
        return redirect(url_for("show_results"), 200)
    session[picked_url_key].append(mtg_helper.Card(draft_list[session[pick_key]][draft_instance.PICK]).get_scryfall_then_image_url())
    session[pick_key] += 1
    
    return render_template('game.html', 
                           draft=draft_instance, 
                           picked=draft_list[session[pick_key]-1][draft_instance.PICK]
                           )

@app.route('/draft/show_results', methods=["POST", "GET"])
def show_results():
    return render_template('end_screen.html')


@app.route('/draft/prepare', methods=["POST", "GET"])
def draft_ingest_file(error=None):
    if error:
        return render_fail_case("something went wrong")
    if request.method == 'POST':
        f = request.files['file']
        if not f:
            return render_fail_case("file shows as nil")
        print("filename shows as " + f.filename)
        f.save(f.filename)
        session[draft_key] = f.filename
        return redirect(url_for(endpoint="draft_play"), 200)
    return render_template('draft_getter.html')

if __name__ == "__main__":
    app.run(debug=True)