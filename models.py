from database import db


film_contract_table=db.Table('film_contract',
    db.Column('user_id',db.String(50),db.ForeignKey('users.uid')),
    db.Column('film_id',db.Integer,db.ForeignKey('films.id'))
)


class User(db.Model):
    __tablename__ = 'users'

    query = db.session.query_property()

    uid = db.Column(db.String(50), primary_key=True)
    films = db.relationship('Film',back_populates='users',lazy='dynamic',secondary=film_contract_table)
    d_service = db.relationship('DrawService',uselist=False, back_populates='user',cascade="save-update, delete")

    def __repr__(self):
        return '<User:{}>'.format(self.uid)


class DrawService(db.Model):
    __tablename__ = 'ds_lists'

    uid = db.Column(db.String(50),db.ForeignKey('users.uid'),primary_key=True)
    flag = db.Column(db.Boolean,default=False)
    count = db.Column(db.Integer,default=0)
    user = db.relationship('User')

    def __repr__(self):
        return '<DrawServiceList:{},{},{}>'.format(self.uid,self.flag,self.count)


class Film(db.Model):
    __tablename__ = 'films'

    query = db.session.query_property()

    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    film = db.Column(db.String(32), nullable=False,unique=True)
    episode = db.Column(db.String(32))
    update_time = db.Column(db.DateTime,nullable=False)
    url = db.Column(db.String(64),nullable=False)
    users = db.relationship('User', back_populates='films', lazy='dynamic', secondary=film_contract_table)

    def __repr__(self):
        return '<Film:{},{},{},{},{}>'.format(self.id,self.film,self.episode,self.update_time,self.url)