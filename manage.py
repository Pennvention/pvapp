from pvapp import app, db
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__': 
    manager.run()
