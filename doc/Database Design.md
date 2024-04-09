# Database Design

## DDL Commands
```sql
CREATE TABLE IF NOT EXISTS Users (
    UserID INT PRIMARY KEY,
    Name VARCHAR(255),
    Email VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Professors (
    ProfessorID INT PRIMARY KEY,
    Name VARCHAR(255),
    Department VARCHAR(255),
    RMP_Link VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Courses (
    CourseID INT PRIMARY KEY, --random
    CourseNumber VARCHAR(255), --cs411
    ProfessorID INT,
    Title VARCHAR(255),
    FOREIGN KEY (ProfessorID) REFERENCES Professors(ProfessorID)
);

CREATE TABLE IF NOT EXISTS Ratings (
    RatingID INT PRIMARY KEY,
    Score DECIMAL(5, 2),
    WouldTakeAgain BOOLEAN,
    CourseID INT,
    UserID INT,
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE IF NOT EXISTS Comments (
    CommentID INT PRIMARY KEY,
    Content TEXT,
    CourseID INT,
    UserID INT,
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

```

## Advanced Queries
**Query 1**: Courses with the highest average rating, including the professor's name and department.

```sql
SELECT c.CourseID, c.Title, p.Name AS ProfessorName, p.Department, AVG(r.Score) AS AverageRating
FROM Courses c
JOIN Professors p ON c.ProfessorID = p.ProfessorID
JOIN Ratings r ON c.CourseID = r.CourseID
GROUP BY c.CourseID, c.Title, p.Name, p.Department
ORDER BY AverageRating DESC;
```
**Query 2**: Determine the percentage of users who would take a course again based on ratings for each course, including courses with no ratings. 
```sql
SELECT c.CourseID, c.Title, 
    COALESCE(
    (SELECT ROUND(SUM(CASE WHEN r.WouldTakeAgain THEN 1 ELSE 0 END) * 100.0 / COUNT(r.WouldTakeAgain), 2)
    FROM Ratings r
    WHERE r.CourseID = c.CourseID
    GROUP BY r.CourseID), 
    0) AS PercentageWouldTakeAgain
FROM Courses c
LEFT JOIN Ratings r ON c.CourseID = r.CourseID
GROUP BY c.CourseID, c.Title
ORDER BY PercentageWouldTakeAgain DESC;
```

**Query 3**: Retrieve popular courses, defined by the number of comments and average rating. Include courses with no comments or ratings.
```sql
SELECT c.CourseID, c.Title, p.Name AS ProfessorName,
       COUNT(DISTINCT com.CommentID) AS NumberOfComments,
       COALESCE(AVG(r.Score), 00) AS AverageRating
FROM Courses c
LEFT JOIN Comments com ON c.CourseID = com.CourseID
LEFT JOIN Ratings r ON c.CourseID = r.CourseID
JOIN Professors p ON c.ProfessorID = p.ProfessorID
GROUP BY c.CourseID, c.Title, p.Name
ORDER BY NumberOfComments DESC, AverageRating DESC;
```

**Query 4**: Average GPA of all courses taught by a specific Professor
```sql
SELECT 
    Pr.Name AS ProfessorName,
    Pr.Department,
    AVG(OverallCourseScore) AS AvgProfessorScore
FROM 
    (
        SELECT 
            C.ProfessorID,
            C.Title AS CourseTitle,
            AVG(R.Score) AS OverallCourseScore
        FROM Courses C
        JOIN Ratings R ON C.CourseID = R.CourseID
        GROUP BY C.CourseID
    ) AS CourseScores
JOIN Professors Pr ON CourseScores.ProfessorID = Pr.ProfessorID
GROUP BY Pr.ProfessorID
```

## Database Connection

![Screenshot 2024-04-05 at 3.02.49 PM.png](pics/Screenshot_2024-04-05_at_3.02.49_PM.png)

![Screenshot 2024-04-05 at 3.01.47 PM.png](pics/Screenshot_2024-04-05_at_3.01.47_PM.png)

## Showing the insertion of at least 1000 rows to each table

![Untitled](pics/Untitled.png)

## Top 15 from Advanced Queries:

### Top 15 from Query 1:

![Screen Shot 2024-04-08 at 12.11.41 AM.png](pics/Screen_Shot_2024-04-08_at_12.11.41_AM.png)

### Top 15 from Query 2:

![Screen Shot 2024-04-08 at 12.15.20 AM.png](pics/Screen_Shot_2024-04-08_at_12.15.20_AM.png)

### Top 15 from Query 3:

![Screen Shot 2024-04-08 at 12.09.32 AM.png](pics/Screen_Shot_2024-04-08_at_12.09.32_AM.png)

### Top 15 from Query 4:

![Screen Shot 2024-04-08 at 6.12.00 PM.png](pics/Screen_Shot_2024-04-08_at_6.12.00_PM.png)

## Indexing

### Query 1
 Courses with the highest average rating, including the professor's name and department.

```sql
SELECT c.CourseID, c.Title, p.Name AS ProfessorName, p.Department, AVG(r.Score) AS AverageRating
FROM Courses c
JOIN Professors p ON c.ProfessorID = p.ProfessorID
JOIN Ratings r ON c.CourseID = r.CourseID
GROUP BY c.CourseID, c.Title, p.Name, p.Department
ORDER BY AverageRating DESC;
```

EXPLAIN ANALYZE OUTPUT With Default Index

![Screen Shot 2024-04-07 at 9.50.39 PM.png](pics/Screen_Shot_2024-04-07_at_9.50.39_PM.png)

We can see that the cost is pretty low and the time to run as well. However we can attempt to index.

**Indexing method one**: Index on Courses.ProfessorID

This query joins the Courses table with the Professors table based on the ProfessorID column. An index on Courses.ProfessorID can speed up this join operation by quickly locating all courses taught by each professor. This is particularly beneficial because the join condition directly references Courses.ProfessorID, making lookups based on this column frequent and critical for the join performance.

```sql
CREATE INDEX index_courses_professorid ON Courses(ProfessorID);
```

EXPLAIN ANALYZE OUTPUT Index 1

![Screen Shot 2024-04-07 at 9.58.30 PM.png](pics/Screen_Shot_2024-04-07_at_9.58.30_PM.png)

There doesn’t seem to be any change and there is no index lookup using the index so the index doesn’t seem to help at all.

**Indexing method two**: Index on Ratings.CourseID

The query also involves a join between the Courses and Ratings tables on the CourseID column, followed by an aggregation operation to calculate the average rating. An index on Ratings.CourseID will let there be faster matching of ratings to courses, which is essential for both the join operation and the subsequent aggregation. Since this column is used for a key operation, an index here can greatly reduce the amount of data the database needs to scan, improving query performance.

```sql
CREATE INDEX index_ratings_courseid ON Ratings(CourseID);

```

EXPLAIN ANALYZE OUTPUT Index 2

![Screen Shot 2024-04-07 at 11.01.21 PM.png](pics/Screen_Shot_2024-04-07_at_11.01.21_PM.png)

The cost stays the same and time changes a bit but this indexing also doesn’t change anything. The index still isn't being reached. 

**Indexing method three**: Index on Ratings.CourseID

An index on both CourseID and Score in the Ratings table could further optimize the performance of the average function used on Score in the query. This index supports the join operation by CourseID and could optimizes the calculation of the average score. The database might be able to use the index to directly compute the average without having to sort or scan the entire Score column for each course.

```sql
CREATE INDEX index_rating_ID_Score ON Ratings(CourseID, Score);

```

EXPLAIN ANALYZE OUTPUT Index 3

![Screen Shot 2024-04-07 at 11.11.25 PM.png](pics/Screen_Shot_2024-04-07_at_11.11.25_PM.png)

Here we can see that there is an index scan on index_rating_ID_Score and that there is no effect on the cost at all. This is likely because there are only 1000 rows in the data and there isn’t a big change that indexing makes. 

**Result**:

We will choose indexing on Ratings(CourseID, Score) since we can see that the index is being scanned in the Explain Analyze output. However there really isn’t much of a change overall. 

### Query 2

Determine the percentage of users who would take a course again based on ratings for each course, including courses with no ratings. 

```sql
SELECT c.CourseID, c.Title, 
    COALESCE(
    (SELECT ROUND(SUM(CASE WHEN r.WouldTakeAgain THEN 1 ELSE 0 END) * 100.0 / COUNT(r.WouldTakeAgain), 2)
    FROM Ratings r
    WHERE r.CourseID = c.CourseID
    GROUP BY r.CourseID), 
    0) AS PercentageWouldTakeAgain
FROM Courses c
LEFT JOIN Ratings r ON c.CourseID = r.CourseID
GROUP BY c.CourseID, c.Title
ORDER BY PercentageWouldTakeAgain DESC;
```

EXPLAIN ANALYZE OUTPUT With Default Index

![Screen Shot 2024-04-07 at 8.39.35 PM.png](pics/Screen_Shot_2024-04-07_at_8.39.35_PM.png)

We notice that the cost seems very extreme so we could benefit from indexing.

**Indexing method one**: Index on Ratings.CourseID

The subquery and the main query's join condition both filter ratings based on courseID. An index on ratings.CourseID would make these operations more efficient by allowing the database engine to quickly locate all ratings for each course. This is particularly beneficial because the where and on clauses directly reference ratings.courseID which means that lookups based on this column are frequent and critical for performance.

```sql
CREATE INDEX index_ratings_courseID ON Ratings(CourseID);
```

EXPLAIN ANALYZE OUTPUT Index 1

![Screen Shot 2024-04-07 at 8.39.57 PM.png](pics/2b75b5ec-5683-4a85-a754-e98f9d3e0b29.png)

We can see that there is a huge cost decrease once indexing on Ratings Course ID.

**Indexing method two:** Index on Course.CourseID
Although courses might be a smaller table compared to ratings, an index on courses.courseID could possibly still enhance the join operation. Since the query involves a left join based on courseID ****and there is a group by on Course ID, the database can benefit from an index on this column in the courses table to quickly map each course to its ratings. This index could help in speeding up the access to course information during the join operation.

```sql
CREATE INDEX index_courses_courseID ON Courses(CourseID);
```

EXPLAIN ANALYZE OUTPUT Index 2

![Screen Shot 2024-04-07 at 8.41.15 PM.png](pics/Screen_Shot_2024-04-07_at_8.41.15_PM.png)

This definitely did not make it better so this indexing method is not good and should not be used.

**Indexing method three:** Index on Rating(CourseID, WouldTakeAgain)

 A composite index that includes both courseID and would take again could further optimize the subquery's performance. This is because the subquery not only filters by courseID but also needs to access the wouldtakeagain attribute to calculate the percentages. With a composite index, the database could efficiently filter and calculate the required information without having to fetch the entire row.

```sql
CREATE INDEX index_ratings_wta_courseid ON Ratings(WouldTakeAgain, CourseID);
```

EXPLAIN ANALYZE OUTPUT Index 3

![Screen Shot 2024-04-07 at 8.44.41 PM.png](pics/Screen_Shot_2024-04-07_at_8.44.41_PM.png)

This also did not have a good performance.

**Result**:

After all three indexes, we see that only indexing on Ratings(CourseID) would be very helpful in decreasing cost as explained by the Explain analyze output. 

### Query 3


Retrieve popular courses, defined by the number of comments and average rating. Include courses with no comments or ratings.'''
```sql
SELECT c.CourseID, c.Title, p.Name AS ProfessorName,
       COUNT(DISTINCT com.CommentID) AS NumberOfComments,
       COALESCE(AVG(r.Score), 00) AS AverageRating
FROM Courses c
LEFT JOIN Comments com ON c.CourseID = com.CourseID
LEFT JOIN Ratings r ON c.CourseID = r.CourseID
JOIN Professors p ON c.ProfessorID = p.ProfessorID
GROUP BY c.CourseID, c.Title, p.Name
ORDER BY NumberOfComments DESC, AverageRating DESC;
```

EXPLAIN ANALYZE OUTPUT With Default Index

![Screen Shot 2024-04-07 at 11.36.41 PM.png](pics/Screen_Shot_2024-04-07_at_11.36.41_PM.png)

We notice that there are a lot of rows being read and the cost is pretty high because of that.

**Indexing method one:** Index on Comments.ProfessorID and Comments.CommentID

Creating a composite index on CourseID and CommentsID in the Comments table could significantly enhance the performance of the given SQL query. Firstly, it optimizes the join operation between the Courses and Comments tables on CourseID, ensuring that the database engine can quickly find all comments related to each course. Secondly, including CommentsID in the index further eases the process of counting distinct comment IDs for each course, as it allows the database engine to efficiently traverse the index to count unique comment IDs without needing to fetch and inspect the full rows from the Comments table.

```jsx
CREATE INDEX index_comments_courseid ON Comments(CourseID, CommentID);
```

EXPLAIN ANALYZE OUTPUT Index 1

![Screen Shot 2024-04-07 at 11.42.21 PM.png](pics/Screen_Shot_2024-04-07_at_11.42.21_PM.png)

The time ends up increasing but we can see that the cost decreases with the stream results. The number of rows read are much less. So this is a pretty good index.

**Indexing method two:** Index on Ratings.CourseID and Ratings.Score

This query involves a join with the ratings table and computes the average score for each course. A composite index on course and score can quicken these operations. The courseID is used for the join, and scores is involved in calculating the average of scores. While courseID helps in quickly locating the ratings relevant to each course, including score in the index might help the database engine more efficiently calculate the average.

```sql
CREATE INDEX index_ratings_courseid_score ON Ratings(CourseID, Score);
```

EXPLAIN ANALYZE OUTPUT Index 2

![Screen Shot 2024-04-07 at 11.55.36 PM.png](pics/Screen_Shot_2024-04-07_at_11.55.36_PM.png)

We can see that cost does decrease but not as much as the previous index. However we could still use this index and have multiple indexes.

**Indexing method three:** Index on Courses.ProfessorID

This query joins the Courses table with the Professors table using ProfessorID. An index on Courses.ProfessorID will make this join operation faster by reducing the time needed to find matching rows in the ProfessorID table. This is particularly beneficial because this join is essential for retrieving the ProfessorID for each course, which is a part of the query's SELECT clause.

```sql
CREATE INDEX index_courses_professorID ON Ratings(CourseID, Score);
```

EXPLAIN ANALYZE OUTPUT Index 3

![Screen Shot 2024-04-08 at 12.02.41 AM.png](pics/Screen_Shot_2024-04-08_at_12.02.41_AM.png)

We can see here that the index isn’t being scanned so there is no change in cost and this index does not help at all. 

**Result**:

By combining and making two indexes, one for Comments.ProfessorID and Comments.CommentID and one for Ratings.CourseID and Ratings.Score, we actually decrease cost by a lot as seen below in the Explain Analyze while keeping both indexes.. So the plan is to have two indexes one on the Comments table and one on the ratings table. 

![Screen Shot 2024-04-07 at 11.59.09 PM.png](pics/Screen_Shot_2024-04-07_at_11.59.09_PM.png)

### Query 4
Average GPA of a Professor based on all courses taught by the Professor

```sql
SELECT 
    Pr.Name AS ProfessorName,
    Pr.Department,
    AVG(OverallCourseScore) AS AvgProfessorScore
FROM 
    (
        SELECT 
            C.ProfessorID,
            C.Title AS CourseTitle,
            AVG(R.Score) AS OverallCourseScore
        FROM Courses C
        JOIN Ratings R ON C.CourseID = R.CourseID
        GROUP BY C.CourseID
    ) AS CourseScores
JOIN Professors Pr ON CourseScores.ProfessorID = Pr.ProfessorID
GROUP BY Pr.ProfessorID
```

EXPLAIN ANALYZE OUTPUT With Default Index

![Screen Shot 2024-04-08 at 6.26.47 PM.png](pics/Screen_Shot_2024-04-08_at_6.26.47_PM.png)

**Indexing method one:** Index on Ratings.CourseID

This query joins the Courses table with the Ratingstable on Courses.CourseID. An index on Ratings.CourseID will make this join operation more efficient by quickly locating entries in the Ratings table for corresponding entries in the Courses table. Since courseID is used in a join condition, this index could help in reducing the lookup time significantly.

```sql
CREATE INDEX index_ratings_courseid ON Ratings(CourseID);
```

EXPLAIN ANALYZE OUTPUT With Index 1

![Screen Shot 2024-04-08 at 6.39.59 PM.png](pics/Screen_Shot_2024-04-08_at_6.39.59_PM.png)

Here we can see that there is no effect on the cost with this index and it is not being used at all.

**Indexing method two:** Index on Ratings.Score

This query uses Ratings.Score to calculate the average overall course score for all courses taught by one professor. Because there is an aggregation on this score an index on Ratings.Score could potentially be helpful in de lookup time.

```sql
CREATE INDEX index_ratings_score ON Ratings(score);
```

EXPLAIN ANALYZE OUTPUT With Index 2

![Screen Shot 2024-04-08 at 6.43.04 PM.png](pics/Screen_Shot_2024-04-08_at_6.43.04_PM.png)

Here there is also no effect whatsoever once there is indexing. The index is not even getting scanned. 

**Indexing method three:** Index on Ratings.Score and Ratings.CourseID

Here we decided to index compositely on both Score and CourseID. This is because of the AVG being used on Score and the CourseID being used to join. We think that indexing on these two together could help costs go down.

```sql
CREATE INDEX index_ratings_score_courseid ON Ratings(score,CourseID);
```

EXPLAIN ANALYZE OUTPUT With Index 3

![Screen Shot 2024-04-08 at 6.50.26 PM.png](pics/Screen_Shot_2024-04-08_at_6.50.26_PM.png)

What we found was that there was still no effect on costs or time with this composite index.

**Result**: No indexing strategy really works for this query and helps cut down. This could likely be because many of the possible indexes are already primary keys and thus default indices for this query.