from setuptools import setup

# List of dependencies installed via `pip install -e .`
# by virtue of the Setuptools `install_requires` value below.
requires = [
    "alembic",
    "bcrypt",
    "cerberus",
    "pymysql",
    "click",
    "cryptography",
    "pyramid",
    "pyramid_jinja2",
    "pyramid_tm",
    "pyramid_retry",
    "pyyaml",
    "redis",
    "sqlalchemy",
    "waitress",
    "zope.sqlalchemy",
]

dev_requires = [
    "pytest",
    "pytest-mock",
    "webtest",
]

setup(
    name="codechallenge",
    install_requires=requires,
    extras_require={
        "dev": dev_requires,
    },
    entry_points={
        "paste.app_factory": ["main = codechallenge:main"],
    },
)
