import click
from nativ import app, db, mail
from flask_mail import Message
from nativ.models import User, Post, Comment

@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        click.confirm('This operation will delete the database, do you want to continue?', abort=True)
        db.drop_all()
        click.echo('Drop tables.')
    db.create_all()
    click.echo('Initialized database.')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Post=Post, Comment=Comment, mail=mail, Message=Message)


@app.cli.command()
@click.option('--user', default=30, help='用户数量，默认为30')
@click.option('--post', default=300, help='文章数量，默认为300')
@click.option('--comment', default=5000, help='评论数量，默认为5000')
def forge(user, post, comment):
    '''Generating fake data.'''
    from nativ.fakers import fake_user, fake_posts, fake_comments

    db.drop_all()
    db.create_all()

    click.echo('生成 %d 用户中...' % user)
    fake_user(user)

    click.echo('生成 %d 文章中...' % post)
    fake_posts(post)

    click.echo('生成 %d 评论中...' % comment)
    fake_comments(comment)

    click.echo('完成')

