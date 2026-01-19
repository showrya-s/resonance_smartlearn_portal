import sqlite3

# Connect to database (will create if it doesn't exist)
db = sqlite3.connect("database.db")
cur = db.cursor()

# ------------------ CREATE TABLES ------------------
cur.executescript("""
-- students table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    name TEXT,
    class INTEGER,
    section TEXT,
    roll INTEGER,
    attendance INTEGER,
    photo TEXT
);

-- teachers table
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    name TEXT
);

-- marks table
CREATE TABLE IF NOT EXISTS marks (
    student_id INTEGER,
    subject TEXT,
    exam_type TEXT,
    marks INTEGER
);

-- remarks
CREATE TABLE IF NOT EXISTS remarks (
    student_id INTEGER,
    teacher_remark TEXT,
    ai_remark TEXT
);

-- performance level
CREATE TABLE IF NOT EXISTS performance (
    student_id INTEGER,
    subject TEXT,
    level TEXT
);
""")

# ------------------ INSERT SAMPLE STUDENTS ------------------
cur.execute("""
INSERT OR IGNORE INTO students (username, password, name, class, section, roll, attendance, photo)
VALUES 
('student1', '12345', 'Alice Kumar', 10, 'A', 1, 95, ''),
('student2', '12345', 'Rahul Singh', 10, 'B', 2, 90, '')
""")

# ------------------ INSERT SAMPLE TEACHERS ------------------
cur.execute("""
INSERT OR IGNORE INTO teachers (username, password, name)
VALUES 
('teacher1', '54321', 'Mr. Sharma'),
('teacher2', '54321', 'Ms. Mehta')
""")

# ------------------ INSERT SAMPLE MARKS ------------------
cur.execute("""
INSERT OR IGNORE INTO marks (student_id, subject, exam_type, marks)
VALUES 
(1, 'Maths', 'State', 88),
(1, 'Science', 'State', 92),
(1, 'English', 'State', 75),
(2, 'Maths', 'State', 65),
(2, 'Science', 'State', 70),
(2, 'English', 'State', 60)
""")

# Commit and close
db.commit()
db.close()

print("database.db created and sample data inserted successfully!")
