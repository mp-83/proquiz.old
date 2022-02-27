from codechallenge.entities import Answers, Matches, Questions, Reactions, Users
from codechallenge.exceptions import NotFoundObjectError, ValidateError


class RetrieveObject:
    def __init__(self, uid, otype):
        self.object_uid = uid
        self.otype = otype

    def get(self):
        klass = {
            "answer": Answers,
            "match": Matches,
            "question": Questions,
            "user": Users,
        }.get(self.otype)

        obj = klass.get(uid=self.object_uid)
        if obj:
            return obj
        raise NotFoundObjectError("")


class ValidatePlayLand:
    def __init__(self, **kwargs):
        self.match_uid = kwargs.get("match_uid")
        self.user_uid = kwargs.get("user_uid")

    def valid_match(self):
        match = RetrieveObject(self.match_uid, otype="match").get()
        if match.is_valid:
            return match

        raise ValidateError("Expired match")

    def is_valid(self):
        return {"match": self.valid_match()}


class ValidatePlayStart:
    def __init__(self, **kwargs):
        self.match_uid = kwargs.get("match_uid")
        self.user_uid = kwargs.get("user_uid")

    def valid_user(self):
        user = Users.get(uid=self.user_uid)
        if user:
            return user

        raise NotFoundObjectError("Invalid user")

    def valid_match(self):
        return RetrieveObject(self.match_uid, otype="match").get()

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
        self.match_uid = kwargs.get("match_uid")
        self.answer_uid = kwargs.get("answer_uid")
        self.user_uid = kwargs.get("user_uid")
        self.question_uid = kwargs.get("question_uid")
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
        match = RetrieveObject(self.match_uid, otype="match").get()
        self._data["match"] = match

    def is_valid(self):
        # expected to run in sequence
        self.valid_answer()
        self.valid_user()
        self.valid_match()
        self.valid_reaction()
        return self._data


class ValidateEditMatch:
    def __init__(self, match_uid):
        self.match_uid = match_uid

    def valid_match(self):
        match = RetrieveObject(self.match_uid, otype="match").get()
        if not match.is_started:
            return match

        raise ValidateError("Invalid answer")

    def is_valid(self):
        return self.valid_match()
