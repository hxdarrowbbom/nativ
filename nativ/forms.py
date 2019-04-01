from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField, \
    PasswordField, BooleanField, FileField
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired, Length, Email, \
    EqualTo, ValidationError, regexp
from flask_ckeditor import CKEditorField
from flask_uploads import IMAGES


class valiPassword(object):
    def __init__(self, message=None):
        if not message:
            message = '需要包含大写字母、小写字母'
        self.message = message

    def __call__(self, form, field):
        data = field.data
        upper = lower = False
        for i in data:
            if i <= 'Z' and i >= 'A':
                upper = True
            elif i <='z' and i >= 'a':
                lower = True
            elif i >= '}' or i <= '!':
                raise ValidationError('包含非法字符')
        if not (upper and lower):
            raise ValidationError(self.message)


class NativForm(FlaskForm):
    body = TextAreaField('源文本:', validators=[DataRequired()])
    submit = SubmitField()


class ProfileForm(FlaskForm):
    avatar = FileField('头像.*', validators=[FileAllowed(IMAGES, message='上传的头像文件类型错误,请重新上传！')])
    about_me = TextAreaField('个性签名', validators=[DataRequired()])
    submit = SubmitField('保存')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message='请输入合法的邮件地址')])
    password = PasswordField('密码', validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField('记住')
    submit = SubmitField('登陆')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(2, 10, message='用户名须控制在2-10个字符')])
    email = StringField('email', validators=[DataRequired(), Email(message='请输入合法的邮件地址')])
    password = PasswordField('密码', validators=[DataRequired(), Length(8, 16, message='密码须控制在8-16个字符'), valiPassword()])
    password_repeate = PasswordField('重复密码', validators=[EqualTo('password', message="两次密码不一致")])
    submit = SubmitField('注册')


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(2, 60, message='标题须控制在2-60个字符')])
    body = CKEditorField('正文', validators=[DataRequired(), Length(min=60, message='正文须大于60个字符')])
    submit = SubmitField('发布')


class CommentForm(FlaskForm):
    body = TextAreaField('评论', validators=[DataRequired(), Length(2,255, message='不得大于255个字符')])
    submit = SubmitField('回复')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[Email(message='请输入合法的邮件地址')])
    submit = SubmitField('确认')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('密码', validators=[DataRequired(), Length(8, 16, message='密码须控制在8-16个字符'), valiPassword()])
    password_repeate = PasswordField('重复密码', validators=[EqualTo('password', message="两次密码不一致")])
    submit = SubmitField('重置密码')
