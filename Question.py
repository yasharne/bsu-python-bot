import pprint
class Question:
    def __init__(self, data):
        self.question = data['question']
        self.id = data['id']
        self.score = data['score']
        self.correct_answer = data['correct_answer']
        self.answers = []
        for answer in data['answers']:
            self.answers.append(answer['value'])

    def get_id(self):
        return self.id

    # def get_question(self):
    #     return self.question
    #
    # def get_correct_answer(self):
    #     return self.correct_answer
    #
    # def get_answers(self):
    #     return self.answers

    def get_score(self):
        return self.score