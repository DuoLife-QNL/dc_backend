DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS exam;
DROP TABLE IF EXISTS user_exam;
DROP TABLE IF EXISTS paper;
DROP TABLE IF EXISTS answer;
DROP TABLE IF EXISTS std_answer;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE exam(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  description TEXT
);

CREATE TABLE user_exam(
  user_id INTEGER,
  exam_id INTEGER,
  PRIMARY KEY(
    user_id,
    exam_id
  )
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (exam_id) REFERENCES exam(id)
);

CREATE TABLE paper(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  exam_id INTEGER,
  book INTEGER,
  page INTEGER,
  path TEXT NOT NULL,
  FOREIGN KEY (exam_id) REFERENCES exam(id)
);

CREATE TABLE answer(
  paper_id INTEGER,
  problem_no INTEGER,
  content TEXT,
  PRIMARY KEY(
    paper_id,
    problem_no
  ),
  FOREIGN KEY (paper_id) REFERENCES paper(id)
);

CREATE TABLE std_answer(
  exam_id INTEGER, 
  problem_no INTEGER,
  problem_score INTEGER,
  content TEXT,
  PRIMARY KEY(
    exam_id,
    problem_no
  ),
  FOREIGN key (exam_id) REFERENCES exam(id)
);