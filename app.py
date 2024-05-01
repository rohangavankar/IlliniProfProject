from flask import Flask, jsonify, render_template, request, redirect, url_for
import os
from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import text
import jinja2

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
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        bio = request.form['bio']
        courses = [course.strip() for course in request.form['courses'].split(',')]
        print(name, department, courses)
        with create_connection_pool().connect() as db_conn:
            try:
                # Start a transaction
                    db_conn.execute(text("START TRANSACTION"))
                    insert_professor_query = text('''
                        INSERT INTO Professors (Name, Department, RMP_Link)
                        VALUES (:name, :department, :rmp_link)
                    ''')
                    result = db_conn.execute(insert_professor_query, {'name': name, 'department': department, 'rmp_link': 'none'})
                    professor_id = result.lastrowid
                    for course in courses:
                        course_number, title = course.split(':')
                        insert_course_query = text('''
                            INSERT INTO Courses (CourseNumber, ProfessorID, Title)
                            VALUES (:course_number, :professor_id, :title)
                        ''')
                        db_conn.execute(insert_course_query, {'course_number': course_number, 'professor_id': professor_id, 'title': title})
                    db_conn.execute(text("COMMIT"))
                    return redirect(url_for('add_professor'))
            except Exception as e:
                db_conn.execute(text("ROLLBACK"))
                print("Error:", e)
                return render_template('error.html', message="An error occurred while adding professor.")
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
    try:
        pool = create_connection_pool()
        with pool.connect() as db_conn:
            # Start a transaction
            db_conn.execute(text("START TRANSACTION"))
            # Fetch professor information
            professor_info = db_conn.execute(text('''
                SELECT ProfessorID, Name AS ProfessorName, Department
                FROM Professors
                WHERE ProfessorID = :prof_id;
            '''), {'prof_id': prof_id}).fetchone()

            # Fetch courses associated with the professor
            courses = db_conn.execute(text('''
                SELECT CourseID, CourseNumber, Title
                FROM Courses
                WHERE ProfessorID = :prof_id;
            '''), {'prof_id': prof_id}).fetchall()

            # Fetch reviews for each course
            reviews_by_course = {}
            for course in courses:
                reviews = db_conn.execute(text('''
                    SELECT CommentID, Content
                    FROM Comments 
                    WHERE CourseID = :course_id;
                '''), {'course_id': course[0]}).fetchall()
                reviews_by_course[course[0]] = reviews

            # Fetch ratings for each course
            ratings = db_conn.execute(text('''
                SELECT CourseID, AVG(Score) AS AverageRating
                FROM Ratings
                WHERE CourseID IN (SELECT CourseID FROM Courses WHERE ProfessorID = :prof_id)
                GROUP BY CourseID;
            '''), {'prof_id': prof_id}).fetchall()
            ratings_by_course = {rating[0]: rating[1] for rating in ratings}

            # Commit the transaction
            db_conn.execute(text("COMMIT"))

        # Render the template with the fetched data
        return render_template('professor_bio.html', professor=professor_info, courses=courses, reviews_by_course=reviews_by_course, ratings_by_course=ratings_by_course)
    except Exception as e:
        db_conn.execute(text("ROLLBACK"))
        print("Error:", e)
        return render_template('error.html', message="An error occurred while fetching professor information.")


@app.route('/add_review', methods=['POST'])
def add_review():
    if request.method == 'POST':
        score = request.form.get('score', type=float)
        would_take_again = request.form.get('would_take_again', type=bool)
        comment = request.form.get('comment')
        course_id = request.form.get('course_id', type=int)
        professor_id = request.form.get('professor_id')

        user_id = 0

        pool = create_connection_pool()

        with pool.connect() as db_conn:
            try:
                result_proxy = db_conn.execute(text('''
                    CALL AddCourseRatingAndComment(:p_UserID, :p_CourseID, :p_Score, :p_WouldTakeAgain, :p_Comment)
                '''), {
                    'p_UserID': user_id, 
                    'p_CourseID': course_id, 
                    'p_Score': score, 
                    'p_WouldTakeAgain': would_take_again, 
                    'p_Comment': comment
                })
                
                result = result_proxy.fetchall()
                if result:
                    print(result[0][0])  

            except Exception as e:
                db_conn.rollback() 
                print(str(e))

            finally:
                db_conn.close()

        return redirect(url_for('professor_bio', prof_id=professor_id))

    
@app.route('/delete_review/<int:prof_id>/<int:id>', methods=['GET'])
def delete_review(prof_id, id):
    pool = create_connection_pool()
    with pool.connect() as db_conn:
        db_conn.execute(text("START TRANSACTION"))
        db_conn.execute(text('''
            DELETE FROM Comments WHERE CommentID = :comment_id
        '''), {'comment_id': id})
        db_conn.execute(text("COMMIT"))
    return redirect(url_for('professor_bio', prof_id=prof_id))

@app.route('/search', methods=['POST'])
def search():
    courseNumber = request.form.get('courseNumber')
    professor = request.form.get('professor')

    query = '''
        SELECT DISTINCT p.ProfessorID, p.Name as ProfessorName
        FROM Professors p
        JOIN Courses c ON p.ProfessorID = c.ProfessorID
    '''
    if professor and courseNumber:
        query += '''
            WHERE p.Name = '{}' 
            AND c.CourseNumber = '{}'
        '''.format(professor, courseNumber)
    elif professor:
        query += '''
            WHERE p.Name = '{}'
        '''.format(professor)
    elif courseNumber:
        query += '''
            WHERE c.CourseNumber = '{}'
        '''.format(courseNumber)
    with create_connection_pool().connect() as db_conn:
        result = db_conn.execute(text(query))
        professors = result.fetchall()

    if len(professors) > 1:
        professor_ids = [row[0] for row in professors]
        professor_names = [row[1] for row in professors]
        # Zip the lists
        professor_data = zip(professor_ids, professor_names)
        return render_template('professor_ids.html', professor_data=professor_data)
    elif len(professors) == 1:
        return redirect(url_for('professor_bio', prof_id=str(professors[0][0])))
    else:
        return render_template('no_results.html')

@app.route('/add_rating', methods=['POST'])
def add_rating():
    if request.method == 'POST':
        create_trigger()
        pool = create_connection_pool()
        rating = request.form.get('rating')
        course_id = request.form.get('course_id')
        professor_id = request.form.get('professor_id')
        user_id = 0 
        print(rating, course_id, professor_id)
        with pool.connect() as db_conn:
            query = '''
            INSERT INTO Ratings (Score, CourseID, UserID)
            VALUES ('{}', '{}', '{}');
            '''.format(rating, course_id, user_id)
            db_conn.execute(text(query))
            db_conn.commit()
        
        return redirect(url_for('professor_bio', prof_id=professor_id))
    

def create_trigger():
    pool = create_connection_pool()

    with pool.connect() as db_conn:
        db_conn.execute(text('''DROP TRIGGER IF EXISTS InsertAverageRating'''))
        db_conn.execute(text('''
            CREATE TRIGGER InsertAverageRating
            AFTER INSERT ON Ratings
            FOR EACH ROW
            BEGIN
                DECLARE avg_rating DECIMAL(5, 2);
                DECLARE course_id INT;
                SET course_id = NEW.CourseID;
                SELECT AVG(Score) INTO avg_rating FROM Ratings WHERE CourseID = course_id;
                UPDATE Courses SET AverageRating = avg_rating WHERE CourseID = course_id;
            END;
        '''))
        db_conn.execute(text('''DROP TRIGGER IF EXISTS DeleteAverageRating'''))
        db_conn.execute(text('''
            CREATE TRIGGER DeleteAverageRating
            AFTER DELETE ON Ratings
            FOR EACH ROW
            BEGIN
                DECLARE avg_rating DECIMAL(5, 2);
                DECLARE course_id INT;
                SET course_id = OLD.CourseID;
                SELECT AVG(Score) INTO avg_rating FROM Ratings WHERE CourseID = course_id;
                UPDATE Courses SET AverageRating = avg_rating WHERE CourseID = course_id;
            END;
        '''))
        db_conn.execute(text('''DROP TRIGGER IF EXISTS UpdateAverageRating'''))
        db_conn.execute(text('''
            CREATE TRIGGER UpdateAverageRating
            AFTER UPDATE ON Ratings
            FOR EACH ROW
            BEGIN
                DECLARE avg_rating DECIMAL(5, 2);
                DECLARE course_id INT;
                SET course_id = NEW.CourseID;
                SELECT AVG(Score) INTO avg_rating FROM Ratings WHERE CourseID = course_id;
                UPDATE Courses SET AverageRating = avg_rating WHERE CourseID = course_id;
            END;
        '''))

def create_stored_procedure():
    pool = create_connection_pool()
    with pool.connect() as db_conn:
        db_conn.execute(text('''DROP PROCEDURE IF EXISTS AddCourseRatingAndComment;'''))
        db_conn.execute(text('''
        CREATE PROCEDURE AddCourseRatingAndComment(
            IN p_UserID INT,
            IN p_CourseID INT,
            IN p_Score DECIMAL(5, 2),
            IN p_WouldTakeAgain BOOLEAN,
            IN p_Comment TEXT)
        BEGIN
            DECLARE v_alreadyRated INT;
            SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

            START TRANSACTION;
            SELECT COUNT(*) INTO v_alreadyRated FROM Ratings
            WHERE UserID = p_UserID AND CourseID = p_CourseID;
            
            IF v_alreadyRated = 0 THEN
                IF CHAR_LENGTH(p_Comment) > 10 THEN
                    INSERT INTO Ratings (Score, WouldTakeAgain, CourseID, UserID)
                    VALUES (p_Score, p_WouldTakeAgain, p_CourseID, p_UserID);
                    
                    INSERT INTO Comments (Content, CourseID, UserID)
                    VALUES (p_Comment, p_CourseID, p_UserID);
                    
                    COMMIT;
                    
                    SELECT 'Rating and comment added successfully!' AS Result;
                ELSE
                    ROLLBACK;
                    SELECT 'Comment must be at least 10 characters long.' AS ErrorMessage;
                END IF;
            ELSE
                ROLLBACK;
                SELECT 'User has already rated this course.' AS ErrorMessage;
            END IF;
        END
        '''))
                             

if __name__ == '__main__':
    create_stored_procedure()
    create_trigger()
    app.run(debug=True)
