import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/pvapp/")
activate_this = '/var/www/pvapp/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
from app import app as application
