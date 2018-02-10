from database import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), unique=True)

    observable = db.relationship('Observable', back_populates='user')

    def __repr__(self):
        return '<User:{},{},{}>'.format(self.id,self.user,self.observable)


class Observable(db.Model):
    __tablename__ = 'observables'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(20), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('users.user',ondelete='SET NULL'), nullable=True)

    user = db.relationship('User', back_populates='observable')

    def __repr__(self):
        return '<Observable:{},{},{}>'.format(self.id,self.name,self.user_id)