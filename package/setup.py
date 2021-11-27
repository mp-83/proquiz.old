from setuptools import setup

# List of dependencies installed via `pip install -e .`
# by virtue of the Setuptools `install_requires` value below.
requires = [
    'pyramid',
    'pyramid_jinja2',
    'waitress',
    'pyramid_tm',
    'pyramid_retry',
    'sqlalchemy',
    'pymysql',
    'cryptography',
    'alembic'
]

dev_requires = [
    'pytest',
    'pytest-mock',
    'webtest',
]

setup(
    name='codechallenge',
    install_requires=requires,
    extras_require={
        'dev': dev_requires,
    },
    entry_points={
        'paste.app_factory': [
            'main = codechallenge:main'
        ],
    }    
)
