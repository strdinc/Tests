# main.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from ui_main_menu import Ui_MainWindow  # Скомпилированный UI главного меню
from ui_create_quiz import Ui_CreateQuizDialog  # Скомпилированный UI создания тестов
from ui_take_quiz import Ui_TakeQuizDialog  # Скомпилированный UI прохождения тестов
from quiz_logic import QuizLogic  # Логика работы с тестами


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Инициализация логики приложения
        self.quiz_logic = QuizLogic()

        # Подключение кнопок к функциям
        self.ui.btn_create_quiz.clicked.connect(self.open_create_quiz)
        self.ui.btn_take_quiz.clicked.connect(self.open_take_quiz)
        self.ui.btn_view_stats.clicked.connect(self.view_statistics)

    def open_create_quiz(self):
        """Открыть форму для создания теста."""
        self.create_quiz_window = CreateQuizWindow(self.quiz_logic)
        self.create_quiz_window.show()

    def open_take_quiz(self):
        """Открыть форму для прохождения теста."""
        tests = self.quiz_logic.db.get_tests()
        if not tests:
            QMessageBox.warning(self, "No Tests", "There are no tests available to take.")
            return

        self.take_quiz_window = TakeQuizWindow(self.quiz_logic)
        self.take_quiz_window.show()

    def view_statistics(self):
        """Показать статистику."""
        tests = self.quiz_logic.db.get_tests()
        if not tests:
            QMessageBox.warning(self, "No Tests", "There are no tests available to view statistics.")
            return

        stats_message = ""
        for test in tests:
            test_id, title = test
            avg_score = self.quiz_logic.get_statistics(test_id)
            stats_message += f"Test: {title}\nAverage Score: {avg_score:.2f}\n\n"

        QMessageBox.information(self, "Statistics", stats_message)


class CreateQuizWindow(QMainWindow):
    def __init__(self, quiz_logic):
        super().__init__()
        self.ui = Ui_CreateQuizDialog()
        self.ui.setupUi(self)

        # Явная инициализация виджетов
        self.ui.lineEdit_question.setVisible(True)
        self.ui.textEdit_options.setVisible(True)
        self.ui.lineEdit_correct_answer.setVisible(True)
        self.ui.btn_add_question.setVisible(True)

        self.quiz_logic = quiz_logic
        self.questions = []  # Список вопросов для нового теста

        # Скрываем кнопку "Save Quiz" при инициализации
        self.ui.btn_save_quiz.setVisible(False)

        # Подключение кнопок к функциям
        self.ui.btn_add_question.clicked.connect(self.add_question)
        self.ui.btn_save_quiz.clicked.connect(self.save_quiz)

    def add_question(self):
        """Добавить вопрос в список."""
        question = self.ui.lineEdit_question.text().strip()
        q_type = self.ui.comboBox_type.currentText().lower().replace(" ", "_")
        options = [opt.strip() for opt in self.ui.textEdit_options.toPlainText().split(",") if opt.strip()]
        correct_answer = self.ui.lineEdit_correct_answer.text().strip()

        # Проверка на заполнение обязательных полей
        if not question or not correct_answer:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        # Добавление вопроса в список
        self.questions.append({
            "question": question,
            "type": q_type,
            "options": options,
            "correct_answer": correct_answer
        })

        QMessageBox.information(self, "Success", "Question added successfully!")

        # Показываем кнопку "Save Quiz", если это первый вопрос
        if len(self.questions) == 1:
            self.ui.btn_save_quiz.setVisible(True)

        self.clear_fields()

    def save_quiz(self):
        """Сохранить тест в базу данных."""
        title = self.ui.lineEdit_title.text().strip()
        if not title or not self.questions:
            QMessageBox.warning(self, "Input Error", "Please provide a title and add at least one question.")
            return

        # Создание теста в базе данных
        self.quiz_logic.create_quiz(title, self.questions)
        QMessageBox.information(self, "Success", "Quiz saved successfully!")

        # Очистка формы после сохранения
        self.questions = []
        self.ui.btn_save_quiz.setVisible(False)  # Скрываем кнопку после сохранения
        self.clear_fields()

    def clear_fields(self):
        """Очистить поля формы."""
        self.ui.lineEdit_question.clear()
        self.ui.textEdit_options.clear()
        self.ui.lineEdit_correct_answer.clear()


class TakeQuizWindow(QMainWindow):
    def __init__(self, quiz_logic):
        super().__init__()
        self.ui = Ui_TakeQuizDialog()
        self.ui.setupUi(self)

        self.quiz_logic = quiz_logic
        self.current_test_id = None
        self.current_question_index = 0
        self.answers = []

        # Загрузка доступных тестов
        self.tests = self.quiz_logic.db.get_tests()
        if not self.tests:
            QMessageBox.warning(self, "Error", "No tests available.")
            self.close()
            return

        self.load_test()

        # Подключение кнопок к функциям
        self.ui.btn_next_question.clicked.connect(self.next_question)
        self.ui.btn_finish_quiz.clicked.connect(self.finish_quiz)

    def load_test(self):
        """Загрузить тест для прохождения."""
        self.current_test_id = self.tests[0][0]  # Берем первый тест из списка
        self.questions = self.quiz_logic.db.get_questions(self.current_test_id)
        self.display_question()

    def display_question(self):
        """Отобразить текущий вопрос."""
        if self.current_question_index >= len(self.questions):
            QMessageBox.information(self, "End of Quiz", "You have answered all questions.")
            return

        question_data = self.questions[self.current_question_index]
        question_text, q_type, options, correct_answer = (
            question_data[2], question_data[3], question_data[4], question_data[5]
        )

        self.ui.label_question.setText(question_text)

        # Очистка предыдущих виджетов
        self.ui.radioButton_option1.setText("")
        self.ui.radioButton_option2.setText("")
        self.ui.radioButton_option3.setText("")
        self.ui.checkBox_option1.setText("")
        self.ui.checkBox_option2.setText("")
        self.ui.lineEdit_answer.clear()

        if q_type == "single_choice":
            self.ui.radioButton_option1.setText(options[0])
            self.ui.radioButton_option2.setText(options[1])
            self.ui.radioButton_option3.setText(options[2])
        elif q_type == "multiple_choice":
            self.ui.checkBox_option1.setText(options[0])
            self.ui.checkBox_option2.setText(options[1])
        elif q_type == "text_answer":
            pass  # Поле ввода текста уже очищено

    def next_question(self):
        """Перейти к следующему вопросу."""
        answer = self.get_user_answer()
        if answer is None:
            QMessageBox.warning(self, "Input Error", "Please provide an answer.")
            return

        self.answers.append(answer)
        self.current_question_index += 1
        self.display_question()

    def get_user_answer(self):
        """Получить ответ пользователя."""
        question_data = self.questions[self.current_question_index]
        q_type = question_data[3]

        if q_type == "single_choice":
            if self.ui.radioButton_option1.isChecked():
                return self.ui.radioButton_option1.text()
            elif self.ui.radioButton_option2.isChecked():
                return self.ui.radioButton_option2.text()
            elif self.ui.radioButton_option3.isChecked():
                return self.ui.radioButton_option3.text()
        elif q_type == "multiple_choice":
            selected_options = []
            if self.ui.checkBox_option1.isChecked():
                selected_options.append(self.ui.checkBox_option1.text())
            if self.ui.checkBox_option2.isChecked():
                selected_options.append(self.ui.checkBox_option2.text())
            return selected_options
        elif q_type == "text_answer":
            return self.ui.lineEdit_answer.text()

        return None

    def finish_quiz(self):
        """Завершить тест и показать результат."""
        answer = self.get_user_answer()
        if answer is not None:
            self.answers.append(answer)

        score = self.quiz_logic.take_quiz(self.current_test_id, self.answers)
        QMessageBox.information(self, "Quiz Finished", f"Your score: {score}/{len(self.questions)}")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())