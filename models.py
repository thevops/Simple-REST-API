
import peewee

from flask import jsonify


db = peewee.SqliteDatabase('database.db')

class BaseModel(peewee.Model):
    class Meta:
        database = db

class User(BaseModel):
    username = peewee.CharField(unique=True)
    password = peewee.CharField()
    token = peewee.CharField(null=True)


    @property
    def serialize(self):
        data = {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'token': self.token
        }
        return data


class Tag(BaseModel):
    name = peewee.CharField(unique=True)

    @property
    def serialize(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data


class Post(BaseModel):
    author = peewee.ForeignKeyField(User, backref='posts')
    title = peewee.CharField()
    text = peewee.CharField()

    @property
    def serialize(self):
        data = {
            'id': self.id,
            'author': self.author.username,
            'title': self.title,
            'text': self.text,
            'tags': [t.name for t in Tag.select().join(AssociationPostAndTag).join(Post).where(Post.id == self.id)]
        }
        return data


class AssociationPostAndTag(BaseModel):
    post = peewee.ForeignKeyField(Post)
    tag = peewee.ForeignKeyField(Tag)

    # ponizsze nie dziala tak jak powinno
    #class Meta:
    #    primary_key = peewee.CompositeKey('post', 'tag')



if __name__ == "__main__":
    import sys

    MODELS = [User, Tag, Post, AssociationPostAndTag]
    db.connect()
    if len(sys.argv) < 2:
        pass
    elif sys.argv[1] == "create":
        db.create_tables(MODELS)
    elif sys.argv[1] == "drop":
        db.drop_tables(MODELS)
    elif sys.argv[1] == "createsuperuser":
        User.create(username="admin",password="admin")
    else:
        pass
    db.close()
