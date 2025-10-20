"""Package setup configuration."""

from setuptools import find_packages, setup

setup(
    name="flash_cards_learning_app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.5.0",
        "SQLAlchemy>=2.0.0",
        "python-dotenv>=1.0.0",
        "marshmallow>=3.20.0",
        "marshmallow-sqlalchemy>=0.29.0",
    ],
)
