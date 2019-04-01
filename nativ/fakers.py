# -*- coding: utf-8 -*-
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from nativ import db
from nativ.models import User, Post, Comment

fake = Faker()


def fake_user(count=30):
    for i in range(count):
        user = User(
            email=fake.email(),
            username=fake.name(),
            confirmed=True,
            about_me=fake.sentence(),
            last_seen=fake.date_time_this_year()
            )
        user.set_password('Xx3015783')
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=300):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            author=User.query.get(random.randint(1, User.query.count())),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=5000):
    origin = int(count - 0.7)
    for i in range(origin):
        comment = Comment(
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            user_id=User.query.get(random.randint(1, User.query.count())).id,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    replied = count - origin
    for i in range(replied):
        tmpComment = Comment.query.get(random.randint(1, Comment.query.count()))
        comment = Comment(
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            user_id=User.query.get(random.randint(1, User.query.count())).id,
            post=Post.query.get(random.randint(1, Post.query.count())),
            replied=tmpComment,
            replierd_id=tmpComment.user_id
        )
        db.session.add(comment)
    db.session.commit()