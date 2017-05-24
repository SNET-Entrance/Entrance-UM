from distutils.core import setup
from setuptools import find_packages


setup(
    name='entrance',
    version='0.2',
    packages=find_packages(),
    url='http://www.snet.tu-berlin.de/menue/projects/entrance/',
    license='GNU',
    author='Dirk Thatmann, Philip Raschke',
    author_email='d.thatmann@tu-berlin.de, philip.raschke@mailbox.tu-berlin.de',
    description='entrance - Encryption Service Component UM/CM',
    install_requires=['Flask', 'flask-sqlalchemy', 'flask-bootstrap', 'flask-user', 'flask-mail', 'requests',
                      'Flask-OAuthlib', 'beautifulsoup4', 'cssutils', 'html5lib', 'oic', 'Flask-Cache']
)
