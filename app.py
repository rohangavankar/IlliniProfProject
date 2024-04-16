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


@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        data = request.json
        department = data['department']
        courseNumber = data['courseNumber']
        professor = data['professor']
        print("Received:", department, courseNumber, professor)
        results = query_database(department, courseNumber, professor)

def query_database(department, courseNumber, professor):
    # This function should perform a database query based on the parameters
    # For example, you might have SQLAlchemy models and perform a query like:
    # results = Professor.query.filter_by(name=professor, department=department).all()
    # Return a list of dictionaries (or similar structure) that can be JSON serialized
    return [
        {"name": professor, "department": department, "course": courseNumber}
    ]



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


@app.route('/add_professor', methods=['GET', 'POST'])
def add_professor():
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        bio = request.form.get('bio', '')
        new_professor = Professor(name=name, department=department, bio=bio)
        db.session.add(new_professor)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_professor.html')

@app.route('/edit_professor/<int:id>', methods=['GET', 'POST'])
def edit_professor(id):
    professor = Professor.query.get_or_404(id)
    if request.method == 'POST':
        content = request.form['content']
        review = Review(content=content, professor_id=id)
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('edit_professor', id=id))
    return render_template('edit_professor.html', professor=professor)

@app.route('/professors')
def professors():
    professors = Professor.query.all()  # Retrieve all professors from the database
    return render_template('professors.html', professors=professors)

if __name__ == '__main__':
    app.run(debug=True)
