from app_run import app, db
from models import User
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def list_user():
    print(db.session.query(User).all())


if __name__ == '__main__':
    manager.run()