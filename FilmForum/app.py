from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# PostgreSQL bağlantı URL'si doğrudan koda ekleniyor
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://users_db_jxwb_user:3VOng2qo5fW5RK92EAs3sLUsNQY9UeXY@dpg-ctcufpbtq21c7380sbd0-a/users_db_jxwb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = 'flask_secret_key_123'

# Kullanıcı Modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    comments = db.relationship('Comment', backref='user', lazy=True)

# Konu Modeli
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='topics', lazy=True)
    comments = db.relationship('Comment', backref='topic', lazy=True)

# Yorum Modeli
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        new_user = User(username=username, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Kayıt başarılı, giriş yapabilirsiniz!", "success")
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash("Bir hata oluştu, tekrar deneyin.", "error")
            return redirect(url_for('register'))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash("Giriş başarısız, tekrar deneyin.", "error")
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    topics = Topic.query.all()
    return render_template("dashboard.html", topics=topics)

@app.route("/create_topic", methods=["GET", "POST"])
def create_topic():
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        user_id = session.get('user_id')

        if user_id:
            new_topic = Topic(title=title, content=content, user_id=user_id)
            db.session.add(new_topic)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return "Lütfen önce giriş yapın.", 403

    return render_template("create_topic.html")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    app.run(debug=True)
    

    
