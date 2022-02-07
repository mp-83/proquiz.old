from uuid import uuid1

from codechallenge.app import StoreConfig
from codechallenge.entities.game import Game
from codechallenge.entities.meta import Base, TableMixin, classproperty
from codechallenge.entities.question import Question, Questions
from codechallenge.exceptions import NotUsableQuestionError
from sqlalchemy import Boolean, Column, DateTime, Integer, String, select


class Match(TableMixin, Base):
    __tablename__ = "match"

    # implicit backward relations
    # games: rankings: reactions:

    name = Column(String, nullable=False, unique=True)
    url = Column(String, nullable=True)
    # if true, this match is playable only by users with the link
    is_restricted = Column(Boolean, default=True)
    # after this time match is no longer playable
    expires = Column(DateTime(timezone=True), nullable=True)
    # how many times a match can be played
    times = Column(Integer, default=1)
    # when True games should be played in order
    order = Column(Boolean, default=True)

    def __init__(self, **kwargs):
        """
        Initiate the instance

        UUID based on the host ID and current time
        the first 23 chars, are the ones based on
        the time, therefore the ones that change
        every tick and guarantee the uniqueness
        """
        _name = kwargs.get("name")
        if _name is None or _name == "":
            uuid_time_substring = "{}".format(uuid1())[:23]
            kwargs["name"] = f"M-{uuid_time_substring}"
        super().__init__(**kwargs)

    @property
    def session(self):
        return StoreConfig().session

    @property
    def questions(self):
        return [list(g.ordered_questions) for g in self.games]

    def refresh(self):
        self.session.refresh(self)
        return self

    def create(self):
        self.session.add(self)
        self.session.commit()
        return self

    def with_name(self, name):
        matched_row = self.session.execute(select(Match).where(Match.name == name))
        return matched_row.scalar_one_or_none()

    @property
    def ordered_games(self):
        games = {g.index: g for g in self.games}
        _sorted = sorted(games)
        return [games[i] for i in _sorted]

    @property
    def is_started(self):
        return len(self.reactions)

    def update(self, **attrs):
        for name, value in attrs.items():
            if name == "questions":
                self.update_questions(value)
            else:
                setattr(self, name, value)
        self.session.commit()

    def update_questions(self, questions, commit=False):
        """Add or update questions for this match

        Question position is determined based on
        the position within the array
        """
        result = []
        ids = [q.get("uid") for q in questions if q.get("uid")]
        existing = {}
        if ids:
            existing = {q.uid: q for q in Questions.questions_with_ids(*ids).all()}

        for q in questions:
            game_idx = q.get("game")
            if game_idx is None:
                g = Game(match_uid=self.uid).create()
            else:
                g = self.games[game_idx]

            if q.get("uid") in existing:
                question = existing.get(q.get("uid"))
                question.text = q.get("text", question.text)
                question.position = q.get("position", question.position)
                question.code = q.get("code", question.code)
            else:
                question = Question(
                    game_uid=g.uid,
                    text=q.get("text"),
                    position=len(g.questions),
                    code=q.get("code"),
                )
            self.session.add(question)
            result.append(question)

        if commit:
            self.session.commit()
        return result

    def import_template_questions(self, *ids):
        """Import already existsing questions"""
        if not ids:
            return
        questions = Questions.questions_with_ids(*ids).all()
        result = []
        new_game = Game(match_uid=self.uid).create()
        for question in questions:
            if question.game_uid:
                raise NotUsableQuestionError(
                    f"Question with id {question.uid} is already in use"
                )

            new = Question(
                game_uid=new_game.uid,
                text=question.text,
                position=question.position,
                code=question.code,
            )
            self.session.add(new)
            result.append(new)
        self.session.commit()
        return result

    def left_attempts(self, user):
        return len([r for r in self.reactions if r.user.uid == user.uid]) - self.times

    @property
    def json(self):
        """
        Store questions as list, one per game
        """
        return {
            "name": self.name,
            "is_restricted": self.is_restricted,
            "expires": self.expires,
            "order": self.order,
            "times": self.times,
            "questions": [[q.json for q in g.ordered_questions] for g in self.games],
        }


class Matches:
    @classproperty
    def session(self):
        return StoreConfig().session

    @classmethod
    def count(cls):
        return cls.session.query(Match).count()

    @classmethod
    def with_name(cls, name):
        return cls.session.query(Match).filter_by(name=name).one_or_none()

    @classmethod
    def get(cls, uid):
        return cls.session.query(Match).filter_by(uid=uid).one_or_none()
