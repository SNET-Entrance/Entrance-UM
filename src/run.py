from bootstrap import app
import logging
#yourapp/__init__.py

#app = __name__, instance_relative_config=True

# Load the default configuration
#app.config.from_object('config.default')

# Load the configuration from the instance folder
#app.config.from_pyfile('config.py')

# Load the file specified by the APP_CONFIG_FILE environment variable
# Variables defined here will override those in the default configuration
try:
app.config.from_envvar('APP_CONFIG_FILE')
app.config['HAS_CONFIG'] = True
except: 
logging.warning('Can\'t load conf file')
app.config['HAS_CONFIG'] = False
finally:

app.run(host='0.0.0.0')
