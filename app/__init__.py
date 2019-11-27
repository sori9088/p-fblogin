from flask import Flask, redirect, url_for, flash, render_template, jsonify, request
from flask_login import login_required, logout_user, current_user
from .config import Config
from .models import db, login_manager, Token, User
from .oauth import blueprint
from .cli import create_db
from flask_migrate import Migrate
from flask_cors import CORS


app = Flask(__name__)
CORS(app) # Add me after the above line
app.config.from_object(Config)
app.register_blueprint(blueprint, url_prefix="/login")
app.cli.add_command(create_db)
db.init_app(app)
migrate = Migrate(app, db) # this
login_manager.init_app(app)


@app.route("/logout", methods=['GET','POST'])
@login_required
def logout():
    print(request.get_json())
    token = Token.query.filter_by(user_id = current_user.id).first()
    if token:
        db.session.delete(token)
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
def getuser():
    return jsonify({
        "success" : True,
        "user_id" : current_user.id,
        "user_name" : current_user.name 
    })