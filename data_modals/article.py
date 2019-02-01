import app

class Article(app.db.Model):
    __tablename__ = 'articles'
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id
