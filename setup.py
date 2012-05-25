from setuptools import setup
import os

version = '0.1'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

install_requires = [
    'pyramid']

tests_require = [
    'pytest',
    'pytest-pep8']

setup(
    name='pyramid_snippets',
    version=version,
    description='',
    long_description=README + '\n\n' + CHANGES,
    py_modules=[
        'pyramid_snippets'],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'testing': tests_require},
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: Repoze Public License"])
