# quiz_logic.py

from database import QuizDatabase


class QuizLogic:
    def __init__(self):
        self.db = QuizDatabase()

    def create_quiz(self, title, questions):
        """Создание нового теста."""
        test_id = self.db.add_test(title)
        for question in questions:
            self.db.add_question(
                test_id=test_id,
                question=question["question"],
                q_type=question["type"],
                options=question.get("options"),
                correct_answer=question["correct_answer"]
            )

    def take_quiz(self, test_id, answers):
        """Прохождение теста и сохранение результатов."""
        score = 0
        questions = self.db.get_questions(test_id)
        for i, question in enumerate(questions):
            if question[5] == answers[i]:  # Сравнение правильного ответа с ответом пользователя
                score += 1

        # Сохранение результата
        self.db.save_result(user_id=1, test_id=test_id, score=score)
        return score

    def get_statistics(self, test_id):
        """Получение статистики по тесту."""
        self.db.cursor.execute("""
        SELECT AVG(score) FROM results WHERE test_id=?
        """, (test_id,))
        avg_score = self.db.cursor.fetchone()[0]
        return avg_score or 0