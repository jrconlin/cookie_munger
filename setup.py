import io
import os

from setuptools import find_packages, setup


__version__ = "0.1.0"


def read_from(file):
    reply = []
    with io.open(os.path.join(here, file), encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                break
            if line[:2] == '-r':
                reply += read_from(line.split(' ')[1])
                continue
            if line[0] != '#' or line[:2] != '//':
                reply.append(line)
    return reply


here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf8') as f:
    README = f.read()

setup(
    name="cookie_munger",
    version=__version__,
    packages=find_packages(),
    description='Eat cookie, munge cookie, puke cookie',
    long_description=README,
    classifiers=[
        "Topic :: Internet :: WWW/HTTP",
        'Programming Language :: Python',
    ],
    keywords='cookies bad_idea',
    author="JR Conlin",
    author_email="src+cookie@jrconlin.com",
    url='https://github.com/jrconlin/cookie_munger',
    license="MPL2",
    include_package_data=True,
    zip_safe=False,
    install_requires=read_from('requirements.txt'),
    entry_points="""
    [console_scripts]
    munge = cookie_munger.__main__:main
    """,
)
