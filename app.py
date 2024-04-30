from flask import Flask, jsonify, render_template, request, redirect, url_for
import os
from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import text

app = Flask(__name__)

credential_path = "./CRED.json"
root_path = os.getcwd()
credential_path = os.path.join(root_path, "CRED.json")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
DB_USER = "chef"
DB_PASS = "food"
DB_NAME = "omniscient"
INSTANCE_CONNECTION_NAME = "cs-411-nullpointers:us-central1:testbed"


def create_connection_pool():
    connector = Connector()

    def getconn():
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pymysql",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME
        )
        return conn

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return pool

@app.route('/', methods=['GET', 'POST'])
def index():
    pool = create_connection_pool()
    professors = []

    if request.method == 'POST':
        department = request.form.get('department')
        course_number = request.form.get('course_number')
        professor_name = request.form.get('professor')
        
        query = "SELECT * FROM Professors WHERE 1=1"
        
        if department:
            query += " AND department = %s"
        if course_number:
            query += " AND course_number = %s"
        if professor_name:
            query += " AND professor_name = %s"
        with pool.connect() as db_conn:
            result = db_conn.execute(text(query))
            professors = result.fetchall()
        
        return redirect(url_for('index.html'), professors=professors)
    
    return render_template('index.html')

# @app.before_first_request
# def create_tables():
#     db.create_all()

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     conn = get_db_connection()
#     if request.method == 'POST':
#         # name = request.form.get('name')
#         # department = request.form.get('department')
#         # bio = request.form.get('bio')
        
#         # with pool.connect() as db_conn:
#         #     query = text("INSERT INTO Professors (name, department, bio) VALUES (:name, :department, :bio)")
#         #     db_conn.execute(query, {"name": name, "department": department, "bio": bio})
#         #     db_conn.commit()  
        
#         return redirect(url_for('index'))
    
#     professors = []
#     try:
#         with conn.cursor() as cursor:
#             department = request.form.get('department')
#             course_number = request.form.get('course_number')
#             professor = request.form.get('professor')
        
#             query = "SELECT * FROM Professors WHERE 1=1"
        
#             params = {}
#             if department:
#                 query += " AND department = %s"
#                 params['department'] = department
#             if course_number:
#                 query += " AND course_number = %s"
#                 params['course_number'] = course_number
#             if professor:
#                 query += " AND professor = %s"
#                 params['professor'] = professor
            
#             cursor.execute(query, params)
#             professors = cursor.fetchall()
#     finally:
#         conn.close()
    
#     return render_template('index.html', professors=professors)


# @app.route('/search', methods=['POST'])
# def search():
#     if request.method == 'POST':
#         data = request.json
#         department = data['department']
#         courseNumber = data['courseNumber']
#         professor = data['professor']
#         print("Received:", department, courseNumber, professor)
#         results = query_database(department, courseNumber, professor)

# def query_database(department, courseNumber, professor):
#     # This function should perform a database query based on the parameters
#     # For example, you might have SQLAlchemy models and perform a query like:
#     # results = Professor.query.filter_by(name=professor, department=department).all()
#     # Return a list of dictionaries (or similar structure) that can be JSON serialized
    
#     return [
#         {"name": professor, "department": department, "course": courseNumber}
#     ]

# @app.route('/professor/<int:id>', methods=['GET', 'POST'])
# def professor(id):
#     professor = Professor.query.get_or_404(id)
#     if request.method == 'POST':
#         content = request.form.get('content')
#         review = Review(content=content, professor_id=id)
#         db.session.add(review)
#         db.session.commit()
#         return redirect(url_for('professor', id=id))
#     return render_template('professor.html', professor=professor)

# @app.route('/delete_review/<int:id>')
# def delete_review(id):
#     review = Review.query.get_or_404(id)
#     professor_id = review.professor_id
#     db.session.delete(review)
#     db.session.commit()
#     return redirect(url_for('professor', id=professor_id))


@app.route('/add_professor', methods=['GET', 'POST'])
def add_professor():
#     if request.method == 'POST':
#         # name = request.form['name']
#         # department = request.form['department']
#         # bio = request.form.get('bio', '')
#         # new_professor = Professor(name=name, department=department, bio=bio)
#         # db.session.add(new_professor)
#         # db.session.commit()
#         return redirect(url_for('index'))
    return render_template('add_professor.html')

@app.route('/edit_professor/<int:id>', methods=['GET', 'POST'])
def edit_professor(id):
    # professor = Professor.query.get_or_404(id)
    # if request.method == 'POST':
    #     content = request.form['content']
    #     review = Review(content=content, professor_id=id)
    #     db.session.add(review)
    #     db.session.commit()
    #     return redirect(url_for('edit_professor', id=id))
    return render_template('edit_professor.html', professor=[])


@app.route('/get_courses')
def get_courses():
    pool = create_connection_pool()
    with pool.connect() as db_conn:
        result = db_conn.execute(text('''
            SELECT c.CourseID, c.Title, p.Name AS ProfessorName,
                COUNT(DISTINCT com.CommentID) AS NumberOfComments,
                COALESCE(AVG(r.Score), 0) AS AverageRating
            FROM Courses c
            LEFT JOIN Comments com ON c.CourseID = com.CourseID
            LEFT JOIN Ratings r ON c.CourseID = r.CourseID
            JOIN Professors p ON c.ProfessorID = p.ProfessorID
            GROUP BY c.CourseID, c.Title, p.Name
            ORDER BY NumberOfComments DESC, AverageRating DESC;
        ''')).fetchall()
        return jsonify([{"CourseID": cid, "Title": title, "ProfessorName": pname,
                     "NumberOfComments": num_comments, "AverageRating": avg_rating}
                    for cid, title, pname, num_comments, avg_rating in result])

@app.route('/professors')
def professors():
    pool = create_connection_pool()
    professors = []
    with pool.connect() as db_conn:
        professors = db_conn.execute(text('''
            SELECT c.CourseID, c.CourseNumber, c.Title, p.ProfessorID, p.Name AS ProfessorName, p.Department, ROUND(AVG(r.Score), 2) AS AverageRating
            FROM Courses c
            JOIN Professors p ON c.ProfessorID = p.ProfessorID
            JOIN Ratings r ON c.CourseID = r.CourseID
            GROUP BY c.CourseID, c.Title, p.ProfessorID, p.Name, p.Department
            ORDER BY AverageRating DESC;
        ''')).fetchall()
    return render_template('professors.html', professors=professors)

@app.route('/professor/<int:prof_id>', methods=['GET'])
def professor_bio(prof_id):
    pool = create_connection_pool()
    with pool.connect() as db_conn:
        # Fetch professor information and all courses they teach
        professor_info = db_conn.execute(text('''
            SELECT ProfessorID, Name AS ProfessorName, Department
            FROM Professors
            WHERE ProfessorID = :prof_id;
        '''), {'prof_id': prof_id}).fetchone()

        # Fetch all courses taught by this professor
        courses = db_conn.execute(text('''
            SELECT CourseID, CourseNumber, Title
            FROM Courses
            WHERE ProfessorID = :prof_id;
        '''), {'prof_id': prof_id}).fetchall()

        # Fetch reviews for all courses taught by this professor
        reviews_by_course = {}
        for course in courses:
            reviews = db_conn.execute(text('''
                SELECT r.Score, com.Content AS Comment, r.RatingID
                FROM Ratings r
                JOIN Comments com ON r.CourseID = com.CourseID
                WHERE r.CourseID = :course_id;
            '''), {'course_id': course[0]}).fetchall()
            reviews_by_course[course[0]] = reviews
    print(professor_info)
    print(courses)
    print(reviews_by_course)
    return render_template('professor_bio.html', professor=professor_info, courses=courses, reviews_by_course=reviews_by_course)


@app.route('/add_review', methods=['POST'])
def add_review():
    if request.method == 'POST':
        pool = create_connection_pool()
        comment = request.form.get('comment')
        course_id = request.form.get('course_id')
        professor_id = request.form.get('professor_id')
        print(comment, course_id, professor_id)
        user_id = 0 
        with pool.connect() as db_conn:
            db_conn.execute(text('''
                INSERT INTO Comments (Content, CourseID, UserID)
                VALUES (:content, :course_id, :user_id)
            '''), {'content': comment, 'course_id': course_id, 'user_id': user_id})
            db_conn.commit()  
        print('reached')
        return redirect(url_for('professor_bio', prof_id=professor_id))
@app.route('/delete_review/<int:id>', methods=['GET'])
def delete_review(id):
    pool = create_connection_pool()
    with pool.connect() as db_conn:
        db_conn.execute(text('''
            DELETE FROM Ratings WHERE RatingID = :rating_id
        '''), {'rating_id': id})
        db_conn.execute(text('''
            DELETE FROM Comments WHERE RatingID = :rating_id
        '''), {'rating_id': id})
    return redirect(url_for('professor_bio', id=id))

@app.route('/search', methods=['POST'])
def search():
    courseNumber = request.form.get('courseNumber')
    professor = request.form.get('professor')

    print(professor)
    # Create the initial query
    query = '''
        SELECT p.ProfessorID 
        FROM Professors p
        JOIN Courses c ON p.ProfessorID = c.ProfessorID
        WHERE p.Name = :professor
    '''
    params = {}
    # Add conditions based on search criteria
    # Execute the query
    params = {'professor': professor}
    with create_connection_pool().connect() as db_conn:
        result = db_conn.execute(text(query), params)
        professor_id = result.fetchone()
    print(professor_id)
    if professor_id:
        print("reached")
        return redirect(url_for('professor_bio', prof_id=str(professor_id[0])))
    else:
        return render_template('no_results.html')

if __name__ == '__main__':
    app.run(debug=True)
