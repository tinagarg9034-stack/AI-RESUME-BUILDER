from flask import Flask, render_template,request
from models import db, User

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///resume.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]

        from models import User

        new_user = User(
            fullname=fullname,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return "Signup Successful!"

    return render_template("signup.html") 

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            return f"Welcome, {user.fullname}!"
        else:
            return "Invalid Email or Password"

    return render_template("login.html") 

@app.route("/resume")
def resume():
    return render_template("resume.html")
    
with app.app_context():
    db.create_all()    

if __name__ == "__main__":
    app.run(debug=True)