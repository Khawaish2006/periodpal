from flask import Flask, request, jsonify , render_template , redirect , url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)   

app.config['SQLALCHEMY_DATABASE_URI']  = 'mysql+pymysql://root:Khawaish%401002@localhost:3306/periodpal'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Story(db.Model):
    __tablename__ = 'stories'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
class Comment(db.Model):
    __tablename__ = 'comments'  

    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    story = db.relationship('Story', backref='comments')

class Myth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # e.g., Health, Culture, Food
    myth_text = db.Column(db.Text, nullable=False)
    fact_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    return  render_template('index.html')
def contains_bad_words(text):
    bad_words = ["sex", "fuck", "bitch", "slut", "dick", "asshole", "porn", "boobs", "nude"]
    words = text.lower().split()
    return any(bad in word for word in words for bad in bad_words)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        content = request.form["story"]

        if contains_bad_words(content):
            return "Your story contains inappropriate content. Please rephrase.", 400

        new_story = Story(content=content)
        db.session.add(new_story)
        db.session.commit()
        return redirect("/stories")

    return render_template("submit.html")

@app.route("/comment/<int:story_id>", methods=["POST"])
def comment(story_id):
    comment_text = request.form["comment"]

    if contains_bad_words(comment_text):
        return "❌ Inappropriate comment detected. Please rephrase.", 400

    new_comment = Comment(story_id=story_id, comment_text=comment_text)
    db.session.add(new_comment)
    db.session.commit()
    return redirect("/stories")


@app.route("/stories")
def stories():
    all_stories = Story.query.order_by(Story.timestamp.desc()).all()
    return render_template("stories.html", stories=all_stories)

@app.route("/like/<int:story_id>", methods=["POST"])
def like_story(story_id):
    story = Story.query.get_or_404(story_id)
    story.likes += 1
    db.session.commit()
    return redirect(request.referrer or url_for('stories'))

@app.route("/myths")
def myth_buster():
    return render_template("myth.html")

@app.route('/myths/<category>')
def myths_by_category(category):
    myths = Myth.query.filter_by(category=category.capitalize()).all()
    return render_template('myth_category.html', myths=myths, category=category.capitalize())



if __name__ == '__main__':
    app.run(debug=True, port = 5000)
