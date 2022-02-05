from codechallenge.app import StoreConfig
from codechallenge.entities.answer import Answer
from codechallenge.entities.meta import Base, TableMixin, classproperty
from sqlalchemy import Column, ForeignKey, Integer, String, select
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


class Question(TableMixin, Base):
    __tablename__ = "question"

    game_uid = Column(Integer, ForeignKey("game.uid"))
    game = relationship("Game", backref="questions")
    # reactions: implicit backward relation

    text = Column(String(400), nullable=False)
    position = Column(Integer, nullable=False)
    time = Column(Integer)  # in seconds
    content_url = Column(String)
    code = Column(String)

    __table_args__ = (
        UniqueConstraint("game_uid", "position", name="ck_question_game_uid_position"),
    )

    @property
    def session(self):
        return StoreConfig().session

    @property
    def is_open(self):
        return len(self.answers) == 0

    @property
    def is_template(self):
        return self.game_uid is None

    def all(self):
        return self.session.execute(select(Question)).all()

    def at_position(self, position):
        matched_row = self.session.execute(
            select(Question).where(Question.position == position)
        )
        return matched_row.scalar_one_or_none()

    def save(self):
        if self.position is None and self.game:
            self.position = len(self.game.questions)

        self.session.add(self)
        self.session.commit()
        return self

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                continue
            setattr(self, k, v)

        self.session.commit()

    def create_with_answers(self, answers):
        _answers = answers or []
        self.session.add(self)
        # this commit might be avoided, as it is done in the .clone()
        # method but without it, fails
        # https://docs.sqlalchemy.org/en/14/tutorial/orm_related_objects.html#cascading-objects-into-the-session
        self.session.commit()
        for position, _answer in enumerate(_answers):
            self.session.add(
                Answer(
                    question_uid=self.uid,
                    text=_answer["text"],
                    position=position,
                    is_correct=position == 0,
                )
            )
        self.session.commit()
        return self

    def clone(self, many=False):
        new = self.__class__(
            game_uid=self.game.uid if self.game else None,
            text=self.text,
            position=self.position,
            code=self.code,
        )
        self.session.add(new)
        for _answer in self.answers:
            self.session.add(
                Answer(
                    question_uid=new.uid,
                    text=_answer.text,
                    position=_answer.position,
                    is_correct=_answer.position,
                    level=_answer.level,
                )
            )
        if not many:
            self.session.commit()
        return new

    @property
    def json(self):
        return {
            "text": self.text,
            "code": self.code,
            "position": self.position,
            "answers": [a.json for a in self.answers],
        }


class Questions:
    @classproperty
    def session(self):
        return StoreConfig().session

    @classmethod
    def count(cls):
        return cls.session.query(Question).count()

    @classmethod
    def questions_with_ids(cls, *ids):
        return cls.session.query(Question).filter(Question.uid.in_(ids))

    # TODO to pass *values
    @classmethod
    def get(cls, uid):
        matched_row = cls.session.execute(select(Question).where(Question.uid == uid))
        return matched_row.scalar_one_or_none()
