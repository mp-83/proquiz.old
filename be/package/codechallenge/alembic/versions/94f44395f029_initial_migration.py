"""Initial migration

Revision ID: 94f44395f029
Revises:
Create Date: 2022-04-02 16:02:30.070673

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "94f44395f029"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "match",
        sa.Column("uid", sa.Integer(), nullable=False),
        sa.Column("create_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("update_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("name", sa.String(length=23), nullable=False),
        sa.Column("uhash", sa.String(length=5), nullable=True),
        sa.Column("code", sa.String(length=4), nullable=True),
        sa.Column("password", sa.String(length=5), nullable=True),
        sa.Column("is_restricted", sa.Boolean(), nullable=True),
        sa.Column("from_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("to_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("times", sa.Integer(), nullable=True),
        sa.Column("order", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_match")),
        sa.UniqueConstraint("name", name=op.f("uq_match_name")),
    )
    op.create_table(
        "open_answer",
        sa.Column("uid", sa.Integer(), nullable=False),
        sa.Column("create_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("update_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("text", sa.String(length=2000), nullable=False),
        sa.Column("content_url", sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_open_answer")),
    )
    op.create_table(
        "user",
        sa.Column("uid", sa.Integer(), nullable=False),
        sa.Column("create_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("update_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email", sa.String(length=256), nullable=True),
        sa.Column("email_digest", sa.String(length=32), nullable=True),
        sa.Column("token_digest", sa.String(length=32), nullable=True),
        sa.Column("name", sa.String(length=30), nullable=True),
        sa.Column("password_hash", sa.String(length=60), nullable=True),
        sa.Column("key", sa.String(length=32), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_user")),
        sa.UniqueConstraint("email", name=op.f("uq_user_email")),
    )
    op.create_table(
        "game",
        sa.Column("uid", sa.Integer(), nullable=False),
        sa.Column("create_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("update_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("match_uid", sa.Integer(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=True),
        sa.Column("order", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["match_uid"],
            ["match.uid"],
            name=op.f("fk_game_match_uid_match"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_game")),
        sa.UniqueConstraint("match_uid", "index", name="ck_game_match_uid_question"),
    )
    op.create_table(
        "ranking",
        sa.Column("uid", sa.Integer(), nullable=False),
        sa.Column("create_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("update_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_uid", sa.Integer(), nullable=False),
        sa.Column("match_uid", sa.Integer(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["match_uid"], ["match.uid"], name=op.f("fk_ranking_match_uid_match")
        ),
        sa.ForeignKeyConstraint(
            ["user_uid"],
            ["user.uid"],
            name=op.f("fk_ranking_user_uid_user"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_ranking")),
    )
    op.create_table(
        "question",
        sa.Column("uid", sa.Integer(), nullable=False),
        sa.Column("create_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("update_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("game_uid", sa.Integer(), nullable=True),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("time", sa.Integer(), nullable=True),
        sa.Column("content_url", sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(
            ["game_uid"],
            ["game.uid"],
            name=op.f("fk_question_game_uid_game"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_question")),
        sa.UniqueConstraint(
            "game_uid", "position", name="ck_question_game_uid_position"
        ),
    )
    op.create_table(
        "answer",
        sa.Column("uid", sa.Integer(), nullable=False),
        sa.Column("create_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("update_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("question_uid", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column("content_url", sa.String(length=256), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["question_uid"],
            ["question.uid"],
            name=op.f("fk_answer_question_uid_question"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_answer")),
        sa.UniqueConstraint(
            "question_uid", "text", name=op.f("uq_answer_question_uid")
        ),
    )
    op.create_table(
        "reaction",
        sa.Column("uid", sa.Integer(), nullable=False),
        sa.Column("create_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("update_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("match_uid", sa.Integer(), nullable=False),
        sa.Column("question_uid", sa.Integer(), nullable=False),
        sa.Column("answer_uid", sa.Integer(), nullable=True),
        sa.Column("open_answer_uid", sa.Integer(), nullable=True),
        sa.Column("user_uid", sa.Integer(), nullable=False),
        sa.Column("game_uid", sa.Integer(), nullable=False),
        sa.Column("q_counter", sa.Integer(), nullable=True),
        sa.Column("g_counter", sa.Integer(), nullable=True),
        sa.Column("dirty", sa.Boolean(), nullable=True),
        sa.Column("answer_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["answer_uid"],
            ["answer.uid"],
            name=op.f("fk_reaction_answer_uid_answer"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["game_uid"],
            ["game.uid"],
            name=op.f("fk_reaction_game_uid_game"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["match_uid"],
            ["match.uid"],
            name=op.f("fk_reaction_match_uid_match"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["open_answer_uid"],
            ["open_answer.uid"],
            name=op.f("fk_reaction_open_answer_uid_open_answer"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["question_uid"],
            ["question.uid"],
            name=op.f("fk_reaction_question_uid_question"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_uid"],
            ["user.uid"],
            name=op.f("fk_reaction_user_uid_user"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("uid", name=op.f("pk_reaction")),
        sa.UniqueConstraint(
            "question_uid",
            "answer_uid",
            "user_uid",
            "match_uid",
            "create_timestamp",
            name=op.f("uq_reaction_question_uid"),
        ),
    )


def downgrade():
    op.drop_table("reaction")
    op.drop_table("answer")
    op.drop_table("question")
    op.drop_table("ranking")
    op.drop_table("game")
    op.drop_table("user")
    op.drop_table("open_answer")
    op.drop_table("match")
