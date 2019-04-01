from nativ import app, db, nlp
from flask import render_template, redirect, url_for, \
    flash, request, current_app, jsonify, json
from nativ.forms import NativForm, LoginForm, \
    RegisterForm, PostForm, ProfileForm, CommentForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, \
    login_required
from nativ.models import User, Post, Comment
from nativ.utils import redirect_back
from nativ.email import send_password_reset_email, send_register_email
import uuid
import sqlalchemy
from nativ.nativWrapper import tagWrapper, nerWrapper, sentimentWrapper, \
    keywordsWrapper, suggestWrapper, nersWrapper
import os
from datetime import datetime
import pymongo
import random


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('index')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            flash('该邮箱已经注册过', 'danger')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            send_register_email(user)
            flash('检查你的邮箱以验证用户', 'info')
            return redirect('login')
    return render_template('register.html', form=form)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    user = User.verify_confirm_token(token)
    user.confirmed = True
    db.session.commit()
    flash('成功验证邮箱，请登陆', 'success')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('无效的邮箱或密码', 'danger')
            return redirect('login')
        elif user.confirmed == False:
            send_register_email(user)
            flash('检查你的邮箱以验证用户', 'info')
            return redirect('login')
        login_user(user, remember=remember)
        flash('欢迎回到Boson', 'success')
        return redirect_back()
    return render_template('login.html', form=form)



@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user)
        flash('检查你的邮箱以进行密码重置', 'info')
        return redirect('login')
    return render_template('rest_password_request.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect('index')
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('重置密码成功，请登陆!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BOSON_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    comment_sub = Comment.query.group_by(Comment.post_id).with_entities(Comment.post_id, sqlalchemy.func.count(
        Comment.post_id).label('count')).subquery()
    hotposts = db.session.query(Post, comment_sub.c.count).join(comment_sub, Post.id == comment_sub.c.post_id).order_by(
        comment_sub.c.count.desc()).limit(10)
    return render_template('index.html', pagination=pagination, posts=posts, hotposts=hotposts)


@app.route('/faviour')
@login_required
def faviour():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BOSON_POST_PER_PAGE']
    pagination = current_user.followed_posts().paginate(page, per_page)
    posts = pagination.items
    return render_template('faviour.html', pagination=pagination, posts=posts)


@app.route('/test')
def test():
    source = "用了十来天吧，设置好信号覆盖全屋，路由在卧室电脑桌的角落，之前的小米看电视总卡，隔了三堵墙确实难为它。群里很多兄弟都换上了86u，想着跟上大家的脚步，咬咬牙买了这么贵的路由，现在看来效果显著贵有贵的好处。非常满意"
    result, tagSet = tagWrapper(source)
    return jsonify(result)


@app.route('/nativSingle', methods=['GET', 'POST'])
def nativSingle():
    form = NativForm()
    if form.validate_on_submit():
        data = form.body.data
        tag, tagSet = tagWrapper(data)
        ner, nerSet = nerWrapper(data)
        sentiment = sentimentWrapper(data)
        keywords, suggestList = keywordsWrapper(data)
        suggests = suggestWrapper(suggestList)
        return render_template('nativSingle.html', form=form,
                               tag=tag, tagSet=tagSet,
                               ner=ner, nerSet=nerSet,
                               sentiment=sentiment,
                               keywords=keywords,
                               suggests=suggests)

    try:
        comments = ['DreamItPossible', 'ROGWIFI', 'Shawshank']
        mongodb = pymongo.MongoClient(host='localhost', port=27017)
        db = mongodb['comments']
        collection = db[random.choice(comments)]
        len = collection.find().count()
        record = collection.find().skip(random.randint(0, len - 1)).limit(1)[0]
        source = record['content']
    except Exception as e:
        print(e)
    finally:
        mongodb.close()
    form.body.data = source
    tag, tagSet = tagWrapper(source)
    ner, nerSet = nerWrapper(source)
    sentiment = sentimentWrapper(source)
    keywords, suggestList = keywordsWrapper(source)
    suggests = suggestWrapper(suggestList)

    return render_template('nativSingle.html', form=form,
                           tag=tag, tagSet=tagSet,
                           ner=ner, nerSet=nerSet,
                           sentiment=sentiment,
                           keywords=keywords,
                           suggests=suggests)



@app.route('/nativMulti', methods=['GET', 'POST'])
def nativMulti():
    form = NativForm()
    if form.validate_on_submit():
        source = form.body.data
        ners, nersSet = nersWrapper(source)
        return render_template('nativMulti.html', form=form, ners=ners, nersSet=nersSet)
    try:
        comments = ['DreamItPossible', 'ROGWIFI', 'Shawshank']
        mongodb = pymongo.MongoClient(host='localhost', port=27017)
        db = mongodb['comments']
        source = ''
        for i in range(20):
            collection = db[random.choice(comments)]
            len = collection.find().count()
            record = collection.find().skip(random.randint(0, len - 1)).limit(1)[0]
            tmpSource = record['content']
            source += tmpSource + '\r\n'
    except Exception as e:
        print(e)
    finally:
        mongodb.close()
    form.body.data = source
    ners, nersSet = nersWrapper(source)
    return render_template('nativMulti.html', form=form, ners=ners, nersSet=nersSet)


@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    form = ProfileForm()
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BOSON_POST_PER_PAGE']
    pagination = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    if form.validate_on_submit():
        if form.avatar.data:
            sourcefilename = form.avatar.data.filename
            tmpfilename = os.path.splitext(sourcefilename)
            filenameEtx =  tmpfilename[1] if tmpfilename[1] != '' else tmpfilename[0]
            filename = str(uuid.uuid4()) + filenameEtx
            form.avatar.data.save(os.path.join(app.config['AVATAR_FOLDER'], filename))
            user.avatar = url_for('static', filename='avatar/' + filename)
        user.about_me = form.about_me.data
        db.session.commit()
        flash('用户资料保存成功', 'success')
        return redirect(url_for('profile', user_id=user.id))
    form.about_me.data = user.about_me
    return render_template('profile.html', form=form, user=user, posts=posts, pagination=pagination)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        post = Post(title=title, body=body, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('文章发布成功', 'success')
        return redirect(url_for('index'))
    return render_template('new_post.html', form=form)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash('文章编辑成功', 'success')
        return redirect(url_for('show_post', post_id=post_id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BOSON_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).order_by(Comment.timestamp.desc()).paginate(
        page, per_page)
    comments = pagination.items
    form = CommentForm()
    if form.validate_on_submit():
        body = form.body.data
        # comment = Comment(body=body, post=post, replier=current_user)
        comment = Comment(body=body, post=post, replier=current_user, replierd=post.author)
        db.session.add(comment)
        db.session.commit()
        flash('评论发布成功', 'success')
        return redirect(url_for('show_post', post_id=post_id))
    return render_template('post.html', post=post, pagination=pagination, comments=comments, form=form)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit() ##--提交
    flash('成功删除文章', 'success')
    return redirect_back()

@app.route('/message')
@login_required
def message():
    form = CommentForm()

    per_page = current_app.config['BOSON_COMMENT_PER_PAGE']

    commentPage = request.args.get('page', 1, type=int)
    commentPagi = User.query.get_or_404(current_user.id).comments.order_by(Comment.timestamp.desc()).paginate(
        commentPage,per_page)
    comments = commentPagi.items

    repliedPage = request.args.get('repliedPage', 1, type=int)
    repliedPagi = User.query.get_or_404(current_user.id).replierds.filter(Comment.user_id!=current_user.id)\
        .order_by(Comment.timestamp.desc()).paginate(repliedPage,per_page)
    replieds = repliedPagi.items

    return render_template('message.html', form=form, comments=comments, commentPagi=commentPagi, replieds=replieds, repliedPagi=repliedPagi)



@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('成功删除评论', 'success')
    return redirect_back()


@app.route('/comment/<int:comment_id>/reply', methods=['POST'])
@login_required
def reply_comment(comment_id):
    post_id = request.args.get('post_id')
    replierd_id = request.args.get('replierd_id')
    commentd = Comment.query.get(comment_id)
    body = request.form['body']
    comment = Comment(body=body, user_id=current_user.id, post_id=int(post_id),
              replierd_id=int(replierd_id), replied=commentd)
    db.session.add(comment)
    db.session.commit()
    flash('成功回复评论', 'success')
    return redirect_back()


@app.route('/user/<int:user_id>/follow')
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)

    if current_user.is_following(user):
        current_user.unfollow(user)
        db.session.commit()
        return jsonify({'text': '关注',})
    else:
        current_user.follow(user)
        db.session.commit()
        return jsonify({'text': '取消关注'})



@app.route('/user/<int:user_id>/followers')
@login_required
def followers(user_id):
    user = User.query.get_or_404(user_id)
    users = user.followers
    return render_template('followers.html', users=users, flag=1)


@app.route('/user/<int:user_id>/followeds')
@login_required
def followeds(user_id):
    user = User.query.get_or_404(user_id)
    users = user.followed
    return render_template('followers.html', users=users, flag=0)

