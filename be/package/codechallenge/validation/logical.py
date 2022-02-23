from codechallenge.entities import Answers, Matches, Questions, Users
from codechallenge.exceptions import NotFoundObjectError, ValidateError


class ValidatePlayNext:
    def __init__(self, **kwargs):
        self.match_uid = kwargs.get("match")
        self.answer_uid = kwargs.get("answer")
        self.user_uid = kwargs.get("user")
        self.question_uid = kwargs.get("question")
        self._data = {}

    def data(self):
        return self._data

    def valid_answer(self):
        answer = Answers.get(uid=self.answer_uid)
        if answer is None:
            raise NotFoundObjectError("Unexisting answer")

        question = Questions.get(uid=self.question_uid)
        if question and answer in question.answers:
            self._data["answer"] = answer
            return

        raise ValidateError("Invalid answer")

    def valid_user(self):
        user = Users.get(uid=self.user_uid)
        if user:
            self._data["user"] = user
            return

        raise NotFoundObjectError("Invalid user")

    def valid_match(self):
        match = Matches.get(uid=self.match_uid)
        if match:
            self._data["match"] = match
            return

        raise NotFoundObjectError("Invalid match")

    def is_valid(self):
        self.valid_answer()
        self.valid_user()
        self.valid_match()
        return self._data
