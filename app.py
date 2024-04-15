from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    reviews = db.relationship('Review', backref='professor', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('department')
        bio = request.form.get('bio')
        professor = Professor(name=name, department=department, bio=bio)
        db.session.add(professor)
        db.session.commit()
        return redirect(url_for('index'))
    professors = Professor.query.all()
    return render_template('index.html', professors=professors)

@app.route('/professor/<int:id>', methods=['GET', 'POST'])
def professor(id):
    professor = Professor.query.get_or_404(id)
    if request.method == 'POST':
        content = request.form.get('content')
        review = Review(content=content, professor_id=id)
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('professor', id=id))
    return render_template('professor.html', professor=professor)

@app.route('/delete_review/<int:id>')
def delete_review(id):
    review = Review.query.get_or_404(id)
    professor_id = review.professor_id
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for('professor', id=professor_id))

if __name__ == '__main__':
    app.run(debug=True)
