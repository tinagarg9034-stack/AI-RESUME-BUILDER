from flask import Flask, render_template,request,session,make_response,redirect
from models import db, User , Resume , Contact
from flask import make_response
from reportlab.pdfgen import canvas
import io
import os
from werkzeug.utils import secure_filename
from reportlab.lib.utils import ImageReader

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.secret_key="mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///resume.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

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
            return render_template(
                "dashboard.html",
                fullname=user.fullname
            )
        else:
            return "Invalid Email or Password"

    return render_template("login.html") 

@app.route("/resume", methods=["GET", "POST"])
def resume():

    if request.method == "POST":
        photo = request.files["photo"]

        filename = secure_filename(photo.filename)
        print(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        resume = Resume.query.filter_by(email=request.form["email"]).first()

        if resume:
            resume.name = request.form["name"]
            resume.phone = request.form["phone"]
            resume.skills = request.form["skills"]
            resume.education = request.form["education"]
            resume.experience = request.form["experience"]
            resume.photo = filename
        else:
            resume = Resume(
                name=request.form["name"],
                email=request.form["email"],
                phone=request.form["phone"],
                skills=request.form["skills"],
                education=request.form["education"],
                experience=request.form["experience"],
                photo=filename
            )
            db.session.add(resume)

        db.session.commit()
        session["name"] = request.form["name"]
        session["email"] = request.form["email"]
        session["phone"] = request.form["phone"]
        session["skills"] = request.form["skills"]
        session["education"] = request.form["education"]
        session["experience"] = request.form["experience"]
        session["photo"] = filename
        return render_template(
            "preview.html",
            name=request.form["name"],
            email=request.form["email"],
            phone=request.form["phone"],
            skills=request.form["skills"],
            education=request.form["education"],
            experience=request.form["experience"],
            photo=filename
        )

    return render_template("resume.html")

@app.route("/edit")
def edit():

    resume = Resume.query.filter_by(email=session["email"]).first()

    return render_template("edit.html", resume=resume)

@app.route("/download")
def download_pdf():

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    photo = session.get("photo", "")

    if photo:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], photo)
        if os.path.exists(image_path):
            p.drawImage(image_path, 430, 700, width=100, height=100)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, 800, "Resume")

    p.setFont("Helvetica", 12)

    p.drawString(50, 760, f"Name: {session.get('name', '')}")
    p.drawString(50, 740, f"Email: {session.get('email', '')}")
    p.drawString(50, 720, f"Phone: {session.get('phone', '')}")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 700, "Skills")

    p.setFont("Helvetica", 12)
    p.drawString(50, 680, session.get("skills", ""))

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 650, "Education")

    p.setFont("Helvetica", 12)
    p.drawString(50, 630, session.get("education", ""))

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 600, "Experience")

    p.setFont("Helvetica", 12)
    p.drawString(50, 580, session.get("experience", ""))

    p.save()

    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=resume.pdf"

    return response   
@app.route("/update", methods=["POST"])
def update():

    resume = Resume.query.filter_by(email=request.form["email"]).first()

    resume.name = request.form["name"]
    resume.phone = request.form["phone"]
    resume.skills = request.form["skills"]
    resume.education = request.form["education"]
    resume.experience = request.form["experience"]

    db.session.commit()

    return "Resume Updated Successfully!"

@app.route("/resumes")
def resumes():

    resumes = Resume.query.all()

    return render_template("resumes.html", resumes=resumes)

@app.route("/view/<int:id>")
def view_resume(id):

    resume = Resume.query.get_or_404(id)

    return render_template("view.html", resume=resume)

@app.route("/delete/<int:id>")
def delete_resume(id):
    resume = Resume.query.get_or_404(id)

    db.session.delete(resume)
    db.session.commit()

    return redirect("/view")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        contact = Contact(
            name=request.form["name"],
            email=request.form["email"],
            message=request.form["message"]
        )

        db.session.add(contact)
        db.session.commit()

        return "Message sent successfully!"

    return render_template("contact.html")

@app.route("/messages")
def messages():
    messages = Contact.query.all()
    return render_template("messages.html", messages=messages)

@app.route("/delete-message/<int:id>")
def delete_message(id):
    message = Contact.query.get_or_404(id)

    db.session.delete(message)
    db.session.commit()

    return redirect("/messages")
       
if __name__ == "__main__":
    app.run(debug=True)