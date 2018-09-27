from Question import Question
from queue import Queue


class QuestionSet:

    def __init__(self, data):
        self._id = data['_id']
        self.category = data['category']
        self.name = data['name']
        self.questions = Queue()
        for question in data['questions']:
            q = Question(question)
            self.questions.put(q)
        self.questions_number = self.questions.qsize()

    def number_of_questions(self):
        return self.questions_number

    def number_of_remaining_questions(self):
        return self.questions.qsize()

    def get_question_number(self):
        return (self.number_of_questions() - self.number_of_remaining_questions())

    def get_question(self):
        return self.questions.get()
