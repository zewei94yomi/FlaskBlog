from flask import render_template, request, Blueprint
from flaskblog.models import Post

# create a Blueprint instance
main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int) # 如果url的request中没有包含！或者！是在调用的时候，没有传递， e.g. :url_for('home', page=page_num)，1 is the default value
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)    # 第page页
    return render_template('home.html', posts=posts)


@main.route("/about")
def about():
    return render_template('about.html', title='About')
