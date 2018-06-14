
from flask import Flask

app = Flask(__name__)
#app.config['JSON_AS_ASCII'] = False

# Routing
from api import PostAPI, UserAPI, \
                UserIdPostAPI, TagAPI, \
                TagIdPostAPI, TokenAPI, MergeTag


app.add_url_rule('/posts', view_func=PostAPI.as_view('posts'), methods=['GET','POST'])
app.add_url_rule('/posts/<int:id>', view_func=PostAPI.as_view('posts_id'), methods=['GET','PUT', 'DELETE'])

app.add_url_rule('/users', view_func=UserAPI.as_view('users'), methods=['GET','POST'])
app.add_url_rule('/users/<int:id>', view_func=UserAPI.as_view('users_id'), methods=['GET','PUT', 'DELETE'])
app.add_url_rule('/users/<int:id>/posts', view_func=UserIdPostAPI.as_view('users_id_posts'), methods=['GET', 'DELETE'])

app.add_url_rule('/tags', view_func=TagAPI.as_view('tags'), methods=['GET','POST'])
app.add_url_rule('/tags/<int:id>', view_func=TagAPI.as_view('tags_id'), methods=['GET','PUT', 'DELETE'])
app.add_url_rule('/tags/<int:id>/posts', view_func=TagIdPostAPI.as_view('tags_id_posts'), methods=['GET','DELETE'])
app.add_url_rule('/merge', view_func=MergeTag.as_view('merge_tags'), methods=['POST'])

app.add_url_rule('/tokens', view_func=TokenAPI.as_view('tokens'), methods=['POST','DELETE'])


if __name__ == '__main__':
    app.run(debug=True)



# https://github.com/mmautner/simple_api