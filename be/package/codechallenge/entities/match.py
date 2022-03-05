from datetime import datetime
from random import choices
from string import ascii_letters
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
    uhash = Column(String)
    # if true, this match is playable only by users with the link
    is_restricted = Column(Boolean, default=True)
    # after this time match is no longer playable
    expires = Column(DateTime(timezone=True))
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

        with_hash = kwargs.pop("with_hash", False)
        if with_hash:
            self.uhash = MatchHash().get_hash()
        super().__init__(**kwargs)

    @property
    def session(self):
        return StoreConfig().session

    @property
    def questions(self):
        return [list(g.ordered_questions) for g in self.games]

    @property
    def questions_count(self):
        return sum(len(g.questions) for g in self.games)

    def refresh(self):
        self.session.refresh(self)
        return self

    def save(self):
        self.session.add(self)
        self.session.commit()
        return self

    def with_name(self, name):
        matched_row = self.session.execute(select(Match).where(Match.name == name))
        return matched_row.scalar_one_or_none()

    @property
    def is_valid(self):
        if self.expires:
            return (self.expires - datetime.now()).total_seconds() > 0
        return True

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
                g = Game(match_uid=self.uid).save()
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
        result = []
        if not ids:
            return result

        questions = Questions.questions_with_ids(*ids).all()
        new_game = Game(match_uid=self.uid).save()
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

    # TODO: to fix. It should not count the reaction but the number of completed
    # attempts for this match.
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

    def set_hash(self, value):
        self.uhash = value
        self.save()
        return self


class MatchHash:
    def new_value(self, length):
        return "".join(choices(ascii_letters, k=length))

    def get_hash(self, length=10):
        value = self.new_value(length)
        while Matches.with_uhash(value):
            value = self.new_value(length)

        return value


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

    @classmethod
    def with_uhash(cls, uhash):
        return cls.session.query(Match).filter_by(uhash=uhash).one_or_none()
