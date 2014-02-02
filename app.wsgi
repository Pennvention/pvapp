import sys
activate_this = '/var/www/pvapp/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
sys.path.append(0, '/var/www/pvapp')
from app import app as application
