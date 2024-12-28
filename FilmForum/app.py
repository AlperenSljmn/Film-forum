from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://users_db_jxwb_user:3VOng2qo5fW5RK92EAs3sLUsNQY9UeXY@dpg-ctcufpbtq21c7380sbd0-a.oregon-postgres.render.com/users_db_jxwb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'flask_secret_key_123'

db = SQLAlchemy(app)

ADMIN_EMAIL = "alperensulejman45@gmail.com"

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

@app.route("/")
def home():
    return redirect(url_for('login'))

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
            session['email'] = user.email
            return redirect(url_for('dashboard'))
        else:
            flash("Giriş başarısız, tekrar deneyin.", "error")
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Başarıyla çıkış yaptınız.", "success")
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    topics = Topic.query.all()
    return render_template("dashboard.html", topics=topics)

@app.route("/topic/<int:topic_id>", methods=["GET", "POST"])
def topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if request.method == "POST":
        content = request.form['comment']
        user_id = session.get('user_id')
        if user_id:
            comment = Comment(content=content, user_id=user_id, topic_id=topic_id)
            db.session.add(comment)
            db.session.commit()
            flash("Yorum başarıyla eklendi.", "success")
        else:
            flash("Yorum eklemek için giriş yapmanız gerekiyor.", "error")
        return redirect(url_for('topic', topic_id=topic_id))

    comments = Comment.query.filter_by(topic_id=topic_id).all()
    return render_template("topic.html", topic=topic, comments=comments)

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
            flash("Konu başarıyla oluşturuldu.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Konu oluşturmak için giriş yapmanız gerekiyor.", "error")
            return redirect(url_for('login'))

    return render_template("create_topic.html")

@app.route("/delete_topic/<int:topic_id>", methods=["POST"])
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    user_email = session.get('email')
    if session.get('user_id') == topic.user_id or user_email == ADMIN_EMAIL:
        db.session.delete(topic)
        db.session.commit()
        flash("Konu başarıyla silindi.", "success")
    else:
        flash("Bu konuyu silme yetkiniz yok.", "error")
    return redirect(url_for('dashboard'))

@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    user_email = session.get('email')
    if session.get('user_id') == comment.user_id or user_email == ADMIN_EMAIL:
        db.session.delete(comment)
        db.session.commit()
        flash("Yorum başarıyla silindi.", "success")
    else:
        flash("Bu yorumu silme yetkiniz yok.", "error")
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
