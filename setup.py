from setuptools import setup

setup(
    name="notepad", packages=["notepad", "tests"], test_suite="tests", install_requires=["pytest"]
)

