import time
class Result:
    def __init__(self):
        self.score = 0
        self.answers = dict()

    def set_s_id(self, id):
        self.s_id = id

    def get_s_id(self):
        return self.s_id

    def set_q_id(self, id):
        self.q_id = id

    def get_q_id(self):
        """Get Questionset ID"""
        return self.q_id

    def set_category(self, category):
        self.category = category

    def get_category(self):
        return self.category

    def add_answer(self, id, answer):
        if isinstance(id, str):
            self.answers[id] = answer
        else:
            self.answers[str(id)] = answer

    def get_answers(self):
        return self.answers

    def add_score(self, value):
        self.score += value

    def get_score(self):
        return self.score

    def reset_score(self):
        self.score = 0

    def set_timestamp(self):
        self.timestamp = time.time()

    def set_begin_time(self):
        """
        the beginning of the test
        :return:
        """
        self.start_time = time.time()

    def get_begin_time(self):
        """
        :return: start time
        """
        return self.start_time

    def set_end_time(self):
        """
        the end of the test
        :return:
        """
        self.end_time = time.time()

    def get_end_time(self):
        """

        :return: end time
        """
        return self.end_time