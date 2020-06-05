from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm


# create a Blueprint instance
posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')

# 动态页面，接收参数，如果url不存在，i.e. 用户发送的http请求在posts.route()无法找到
# 甚至不会执行下面的函数
# 逻辑：不需要为每个post都设计指定一个单独的html页面
#      每次有访问时，访问自己都必须带上id
#      route会自动检测url中带上的这个参数id是否在数据库中存在
#      若存在就导向一个通用的页面并传入相应的参数
@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        # 任何人都可以发起请求，但是必须是post的author和发起人请求人是同一个人的时候才可以看
        # 否则就abort（403）
        abort(403)
    # 生成一个form，用于（view和修改）
    form = PostForm()
    # 这里实际上做了两件事：
    #   1. 定义了form的validate_on_submite()函数
    #   2. 添加了if statement
    # 在执行的时候，先判断这个if（validate_on_submit()是否触发）
    if form.validate_on_submit():
        # post是从db中获得的，可以直接修改，然后commit，就可以直接修改数据库
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        # 修改成功，跳到响应页面，并传递参数（/post/<int:post_id>）
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        # 若只是简单的GET而不修改，就返回这个页面的数据，然后在elif语句外面跳到相应页面
        # 正常的流程都是：
        #   1. 用户先通过GET访问修改的页面（并且不可能触发form的submit
        #   2. 页面显示了数据库中的信息
        #   3. 若有POST发送到同一个页面（url），因为本身就接收POST method，然后就处理（见上一个if statement）
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))