from flask import Flask, redirect, url_for, flash, render_template, jsonify, request
from flask_login import login_required, logout_user, current_user
from .config import Config
from .models import db, login_manager, Token, User, Excerpt, Score
from .oauth import blueprint
from .cli import create_db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
CORS(app) # Add me after the above line
app.config.from_object(Config)
app.register_blueprint(blueprint, url_prefix="/login")
app.cli.add_command(create_db)
db.init_app(app)
migrate = Migrate(app, db) # this
login_manager.init_app(app)

db = SQLAlchemy(app)


@app.route("/logout", methods=['GET','POST'])
@login_required
def logout():
    token = Token.query.filter_by(user_id = current_user.id).first()
    if token:
        db.session.commit()
    logout_user()
    flash("You have logged out")
    return jsonify({
        "success" : True
    })


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/getuser", methods=['GET','POST'])
@login_required
def getuser():
    return jsonify({
        "success" : True,
        "user_id" : current_user.id,
        "user_name" : current_user.name 
    })




@app.route('/excerpts')
def excerpts():
    excerpts = Excerpt.query.all()
    jsonized_excerpt_objects_list = []
    for excerpt in excerpts:
        jsonized_excerpt_objects_list.append(excerpt.as_dict())

    return jsonify(jsonized_excerpt_objects_list)


@app.route('/excerpts/random')
@app.route('/scores', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        data = request.get_json()
        score = Score(user_id=1,
                      time=data['time'],
                      wpm=data['wpm'],
                      errors=data['errorCount'],
                      excerpts_id=data['excerpt_id'])
        db.session.add(score)
        db.session.commit()
        excerpt = Excerpt.query.get(data['excerpt_id'])
        scores = Score.query.filter_by(excerpts_id=data['excerpt_id']).order_by(
            Score.wpm.desc()).limit(3)
        count = Score.query.filter_by(excerpts_id=data['excerpt_id']).count()

        res = {
            "excerpt": {
                "id": excerpt.id,
                "body": excerpt.body,
                "scores": {
                    "top": [{
                        'user_id': score.user_id,
                        'time': score.time,
                        'wpm': score.wpm,
                        'errors': score.errors,
                        'exerpts_id': score.excerpts_id
                    } for score in scores],
                    "count":count
                }
            }
        }

        return jsonify(res)
        ## get request => return a list of excerpts
        #below we get a list of class Excerpt
    excerpts = Excerpt.query.all()
    # translate list of classes to lsit of dictionary (object in js)
    response = {"excerpts": [{"id": i.id, "body": i.body} for i in excerpts]}

    return jsonify(response)
