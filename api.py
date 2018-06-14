
from flask import request
from flask.views import MethodView

from peewee import ModelSelect

import hashlib
import time
import json

from models import db, User, Tag, Post, AssociationPostAndTag

# connect to database
db.connect()


# ---------------------------[ auxiliary functions ]-------------------------

def serialize_headers():
    data = {}
    for i in request.headers:
        data[str(i[0])] = str(i[1])
    return {'headers': data}

def response_model(raw_model=None):
    if not raw_model:
        return json.dumps([], ensure_ascii=False, indent=4)

    if not isinstance(raw_model, ModelSelect): # if this is one row
        raw_model = [raw_model]

    data = [one_row.serialize for one_row in raw_model]
    data.append(serialize_headers())
    return json.dumps(data, ensure_ascii=False, indent=4)

def response_dict(data):
    """
    data = dict()
    """
    #data.update(serialize_headers())
    return json.dumps(data, ensure_ascii=False, indent=4)

def get_json_data(*args):
    r = request.get_json(force=True) # ignore mimetype, force parse as JSON
    for arg in args:
        if arg not in r:
            return False
    return r

def auth_token():
    if "Token" not in request.headers:
        return False
    else:
        u = User.select().where(User.token == request.headers['Token']).first()
        return u

# ---------------------------------------------------------------------------


class PostAPI(MethodView):
    def get(self, id=None):
        """ 
        args = {}
        """

        if id:
            try:
                tmp = Post.select().where(Post.id == id).get()
                #tmp_tags = Tag.select().join(AssociationPostAndTag).join(Post).where(Post.id == id)
                #tags = [t for i.name in tmp_tags]
            except:
                return response_model(), 400
        else:
            tmp = Post.select()

        return response_model(tmp)

    def post(self):
        """
        headers = Token
        args = {"title": title, "text": text, "tags": tag1,tag2,tag3,...}
        """

        user = auth_token()
        if not user:
            return response_model(), 401

        req = get_json_data("title", "text", "tags")
        if not req:
            return response_model(), 400

        # author -> this is user from authentication

        # add Post object
        with db.transaction():
            try:
                p = Post(author=user, title=req['title'].encode('utf-8'), text=req['text'].encode('utf-8'))
                p.save()

                for tag in req['tags'].split(","):
                    tmp, _ = Tag.get_or_create(name=tag)
                    apat = AssociationPostAndTag(post=p, tag=tmp)
                    apat.save()
            except:
                db.rollback()
                return response_model(), 400


        return response_model(), 200


    def put(self, id=None):
        """
        headers = Token
        args = {"title": title, "text": text, "tags": tag1,tag2,...}
        """

        user = auth_token()
        if not user:
            return response_model(), 401

        req = get_json_data("title", "text", "tags")
        if not req or not id:
            return response_model(), 400

        # author -> this is user from authentication

        # get Post object and modify
        try:
            p = Post.select().where(Post.id == id).get()
            p.title = req['title']
            p.text = req['text']
            p.save()
        except:
            return response_model(), 404 # NOT FOUND

        # remove old Post-Tag records
        old_tags = AssociationPostAndTag.delete().where(AssociationPostAndTag.post == p)
        old_tags.execute()

        # get Tag objects list
        for tag in req['tags'].split(","):
            tmp, created = Tag.get_or_create(name=tag)
            apat = AssociationPostAndTag(post=p, tag=tmp)
            apat.save()

        return response_model(), 200


    def delete(self, id=None):
        """
        headers = Token
        args = {}
        """

        user = auth_token()
        if not user:
            return response_model(), 401

        if not id:
            return response_model(), 400

        try:
            p = Post.select().where(Post.id == id).get()
            p.delete_instance()

            asso = AssociationPostAndTag.delete().where(AssociationPostAndTag.post == p)
            asso.execute()
        except:
            return response_model(), 400

        return response_model(), 200


class UserAPI(MethodView):
    def get(self, id=None):
        """
        args = {}
        """

        if id:
            try:
                tmp = User.select().where(User.id == id).get()
            except:
                return response_model(), 400
        else:
            tmp = User.select()

        return response_model(tmp)

    def post(self):
        """
        headers = Token
        args = {"username": username, "password": password}
        """

        user = auth_token()
        if not user:
            return response_model(), 400

        req = get_json_data("username")
        if not req:
            return response_model(), 400

        try:
            new_user = User(username=req['username'],password=req['username'])
            new_user.save()
        except:
            return response_model(), 409 # conflict

        return response_model(), 200

    def put(self, id=None):
        """
        headers = Token
        args = {"username": username, "password": password}
        """

        user = auth_token()
        if not user:
            return response_model(), 401

        req = get_json_data("username","password")
        if not req or not id:
            return response_model(), 400


        try:
            u = User.select().where(User.id == id).get()
            u.username = req['username']
            u.password = req['password']
            u.save()
        except:
            return response_model(), 409 # conflict

        return response_model(), 200

    def delete(self, id=None):
        """
        headers = Token
        args = {}
        """

        user = auth_token()
        if not user:
            return response_model(), 401

        if not id:
            return response_model(), 400

        try:
            u = User.get(User.id == id)
            u.delete_instance()
        except:
            return response_model(), 400

        return response_model(), 200


class UserIdPostAPI(MethodView):
    def get(self, id=None):
        """ 
        args = {}
        """

        try:
            user = User.select().where(User.id == id).get()
            posts = user.posts
        except:
            return response_model(), 400

        return response_model(posts)


    def delete(self, id=None):
        """ 
        headers = Token
        args = {}
        """

        user = auth_token()
        if not user:
            return response_model(), 401

        if not id:
            return response_model(), 400

        try:
            posts = Post.delete().where(Post.author == user)
            posts.execute()
        except:
            return response_model(), 400

        return response_model()


class TagAPI(MethodView):
    def get(self, id=None):
        """
        args = {}
        """

        if id:
            try:
                tmp = Tag.select().where(Tag.id == id).get()
            except:
                return response_model(), 400
        else:
            tmp = Tag.select()

        return response_model(tmp)
        
    def post(self):
        """
        args = {"name": name}
        """
        
        user = auth_token()
        if not user:
            return response_model(), 401

        req = get_json_data("name")
        if not req:
            return response_model(), 400

        try:
            t = Tag(name=req['name'])
            t.save()
        except:
            return response_model(), 409 # conflict

        return response_model(), 200



    def put(self, id=None):
        """
        args = {"name": name}
        """
        
        user = auth_token()
        if not user:
            return response_model(), 401

        req = get_json_data("name")
        if not req or not id:
            return response_model(), 400

        try:
            t = Tag.select().where(Tag.id == id).get()
            t.name = req['name']
            t.save()
        except:
            return response_model(), 409 # conflict

        return response_model(), 200

    def delete(self, id=None):
        """
        headers = Token
        args = {}
        """

        user = auth_token()
        if not user:
            return response_model(), 401

        if not id:
            return response_model(), 400

        try:
            t = Tag.get(Tag.id == id)
            t.delete_instance()
        except:
            return response_model(), 400

        return response_model(), 200


class MergeTag(MethodView):
    def post(self):
        """ 
        headers = Token
        args = {"new_tag_name": new_tag_name}
        """
        user = auth_token()
        if not user:
            return response_model(), 401

        req = get_json_data("old_tag_name","new_tag_name")
        if not req or not id:
            return response_model(), 400

        # get all posts with Tag.id
        posts = Post.select().join(AssociationPostAndTag).join(Tag).where(Tag.name == req['old_tag_name'])

        # remove old Post-Tag connection
        for post in posts:
            asso = AssociationPostAndTag.delete().where(AssociationPostAndTag.post == post)
            asso.execute()
        

        new_tag, _= Tag.get_or_create(name=req['new_tag_name'])
        # save Post to new Tag
        for post in posts:
            apat = AssociationPostAndTag(post=post, tag=new_tag)
            apat.save()

        # remove old tag
        t = Tag.select().where(Tag.name == req['old_tag_name']).get()
        t.delete_instance()

        return response_model(),200


class TagIdPostAPI(MethodView):
    def get(self, id=None):
        """ 
        args = {}
        """
        posts = Post.select().join(AssociationPostAndTag).join(Tag).where(Tag.id == id)
        return response_model(posts)


    def delete(self, id=None):
        """ 
        headers = Token
        args = {}
        """
        user = auth_token()
        if not user:
            return response_model(), 401

        if not id:
            return response_model(), 400

        posts = Post.select().join(AssociationPostAndTag).join(Tag).where(Tag.id == id)
        for p in posts:
            p.delete_instance()

        return response_model()


class TokenAPI(MethodView):
    def post(self):
        """
        args = {"username": username, "password": password}
        """
        req = get_json_data("username", "password")
        if not req:
            return response_model(), 400

        u = User.select().where(User.username == req['username'], User.password == req['password']).first()
        if u:
            h = hashlib.md5()
            h.update(str(time.time()).encode('utf-8'))
            u.token = h.hexdigest()
            u.save()
            return response_dict({"token": h.hexdigest()}), 200
        else:
            return response_model(), 401


    def delete(self):
        """
        headers = Token
        args = {"username": username}
        """

        user = auth_token()
        if not user:
            return response_model(), 400

        req = get_json_data("username")
        if not req:
            return response_model(), 400

        if user.username == req['username']:
            user.token = None
            user.save()
        return response_model(), 200

