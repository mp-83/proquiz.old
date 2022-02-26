from codechallenge.entities import Answers, Matches, Questions, Reactions, Users
from codechallenge.exceptions import NotFoundObjectError, ValidateError


class MatchExists:
    def __init__(self, match_uid):
        self.match_uid = match_uid

    def check(self):
        match = Matches.get(uid=self.match_uid)
        if match:
            return match
        raise NotFoundObjectError("")


class ValidatePlayLand:
    def __init__(self, **kwargs):
        self.match_uid = kwargs.get("match")
        self.user_uid = kwargs.get("user")

    def valid_match(self):
        match = MatchExists(self.match_uid).check()
        if match.is_valid:
            return match

        raise ValidateError("Expired match")

    def is_valid(self):
        return {"match": self.valid_match()}


class ValidatePlayStart:
    def __init__(self, **kwargs):
        self.match_uid = kwargs.get("match")
        self.user_uid = kwargs.get("user")

    def valid_user(self):
        user = Users.get(uid=self.user_uid)
        if user:
            return user

        raise NotFoundObjectError("Invalid user")

    def valid_match(self):
        return MatchExists(self.match_uid).check()

    def is_valid(self):
        match = self.valid_match()
        user = self.valid_user()

        accessibility = (
            user.private
            and match.is_restricted
            or not (user.private or match.is_restricted)
        )
        if match.is_valid and accessibility:
            return {"user": user, "match": match}

        raise ValidateError("Invalid match")


class ValidatePlayNext:
    def __init__(self, **kwargs):
        self.match_uid = kwargs.get("match")
        self.answer_uid = kwargs.get("answer")
        self.user_uid = kwargs.get("user")
        self.question_uid = kwargs.get("question")
        self._data = {}

    def valid_reaction(self):
        user = self._data.get("user")
        if not user:
            user = Users.get(uid=self.user_uid)

        question = self._data.get("question")
        if not question:
            question = Questions.get(uid=self.question_uid)

        reaction = Reactions.reaction_of_user_to_question(user, question)
        if reaction and reaction.answer:
            raise ValidateError("Duplicate Reactions")

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
        match = MatchExists(self.match_uid).check()
        self._data["match"] = match

    def is_valid(self):
        # expected to run in sequence
        self.valid_answer()
        self.valid_user()
        self.valid_match()
        self.valid_reaction()
        return self._data
