from uuid import uuid1

from codechallenge.app import StoreConfig
from codechallenge.exceptions import NotUsableQuestionError
from codechallenge.models.game import Game
from codechallenge.models.meta import Base, TableMixin, classproperty
from codechallenge.models.question import Question, Questions
from sqlalchemy import Column, String, select
from sqlalchemy.orm import relationship


class Match(TableMixin, Base):
    __tablename__ = "match"

    name = Column(String, nullable=False, unique=True)
    games = relationship("Game")

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
        result = []
        for g in self.games:
            result.extend(g.questions)
        return result

    def create(self):
        self.session.add(self)
        self.session.commit()
        return self

    def with_name(self, name):
        matched_row = self.session.execute(select(Match).where(Match.name == name))
        return matched_row.scalar_one_or_none()

    def first_game(self):
        for g in self.games:
            if g.index == 1:
                return g

    def import_template_questions(self, *ids):
        if not ids:
            return
        questions = Questions.questions_with_ids(*ids).all()
        result = []
        new_game = Game(index=1, match_uid=self.uid).create()
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
                difficulty=question.difficulty,
            )
            self.session.add(new)
            result.append(new)
        self.session.commit()
        return result

    @property
    def json(self):
        return {"name": self.name, "questions": [q.json for q in self.questions]}


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
