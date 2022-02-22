from codechallenge.entities import Answers, Questions
from codechallenge.exceptions import ValidateError


class ValidatePlayNext:
    def __init__(self, **kwargs):
        self.match_uid = None
        self.answer_uid = None
        self.user_uid = None
        self.question_uid = None
        self._data = {}

    def data(self):
        return self._data

    def valid_answer(self):
        answer = Answers.get(uid=self.answer_uid)
        if answer is None:
            raise ValidateError("Unexisting answer")

        question = Questions.get(self.question_uid)
        if question and answer in question.answers:
            return

        raise ValidateError("Invalid answer")

    def valid_user(self):
        # user = Users.get(uid=data.get("user"))
        pass
