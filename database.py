# database.py

import sqlite3

class QuizDatabase:
    def __init__(self, db_name="quiz.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Создание таблиц в базе данных."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER,
            question TEXT NOT NULL,
            type TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT,
            FOREIGN KEY(test_id) REFERENCES tests(id)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            test_id INTEGER,
            score INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(test_id) REFERENCES tests(id)
        )
        """)
        self.conn.commit()

    def add_test(self, title):
        """Добавление нового теста."""
        self.cursor.execute("INSERT INTO tests (title) VALUES (?)", (title,))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_question(self, test_id, question, q_type, options, correct_answer):
        """Добавление вопроса к тесту."""
        self.cursor.execute("""
        INSERT INTO questions (test_id, question, type, options, correct_answer)
        VALUES (?, ?, ?, ?, ?)
        """, (test_id, question, q_type, options, correct_answer))
        self.conn.commit()

    def get_tests(self):
        """Получение всех тестов."""
        self.cursor.execute("SELECT * FROM tests")
        return self.cursor.fetchall()

    def get_questions(self, test_id):
        """Получение всех вопросов для теста."""
        self.cursor.execute("SELECT * FROM questions WHERE test_id=?", (test_id,))
        return self.cursor.fetchall()

    def save_result(self, user_id, test_id, score):
        """Сохранение результата теста."""
        self.cursor.execute("""
        INSERT INTO results (user_id, test_id, score)
        VALUES (?, ?, ?)
        """, (user_id, test_id, score))
        self.conn.commit()

    def close(self):
        """Закрытие соединения с базой данных."""
        self.conn.close()