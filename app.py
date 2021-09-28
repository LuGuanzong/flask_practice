import os
from threading import Thread

from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email
from flask import Flask, flash, redirect, url_for, render_template, request, send_from_directory
from flask_ckeditor import CKEditor, CKEditorField, upload_success, upload_fail

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'secret string'),
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=('YuqianChuishui', os.getenv('MAIL_USERNAME')),
    CKEDITOR_SERVE_LOCAL=True,  # Flask使用内置的本地资源
    CKEDITOR_HEIGHT=400,
    CKEDITOR_LANGUAGE='zh-cn',
    CKEDITOR_FILE_UPLOADER='upload_for_ckeditor',
    ALLOWED_EXTENSIONS=['png', 'jpg', 'jpeg', 'gif'],
    UPLOAD_PATH=os.path.join(app.root_path, 'uploads')
)

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.makedirs(app.config['UPLOAD_PATH'])

mail = Mail(app)
ckeditor = CKEditor(app)


# 通过smtp服务器进行发送
def send_smtp_mail(subject, to, body):
    message = Message(subject, recipients=[to], body=body)
    mail.send(message)


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_async_mail(subject, to, body):
    message = Message(subject, recipients=[to], body=body)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_subscribe_mail(subject, to, **kwargs):
    message = Message(subject, recipients=[to], sender='Flask Weekly <%s>' % os.getenv('MAIL_USERNAME'))
    message.body = render_template('emails/subscribe.txt', **kwargs)
    message.html = render_template('emails/subscribe.html', **kwargs)
    mail.send(message)


def send_ckeditor_mail(subject, to, html):
    message = Message(subject, recipients=[to])
    message.body = '温馨提示:由于您的浏览器不支持显示html格式的邮件，该邮件内容无法显示'
    message.html = html
    mail.send(message)


class EmailForm(FlaskForm):
    to = StringField('收信人', validators=[DataRequired(), Email()])
    subject = StringField('主题', validators=[DataRequired()])
    body = TextAreaField('正文', validators=[DataRequired()])
    submit_smtp = SubmitField('smtp普通提交')
    submit_async = SubmitField('smtp异步提交')


class SubscribeForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe')


class RichTextForm(FlaskForm):
    to = StringField('收信人', validators=[DataRequired(), Email()])
    subject = StringField('主题', validators=[DataRequired()])
    content = CKEditorField('正文', validators=[DataRequired()])
    submit = SubmitField('submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    if form.validate_on_submit():
        if form.submit_smtp.data:
            to = form.to.data
            subject = form.subject.data
            body = form.body.data
            send_smtp_mail(subject, to, body)
            flash('邮件已直接发送给' + to + ':' + subject)
        else:
            to = form.to.data
            subject = form.subject.data
            body = form.body.data
            send_async_mail(subject, to, body)
            flash('邮件已异步发送给' + to + ':' + subject)
        redirect(url_for('index'))
    return render_template('index.html', form=form)


@app.route('/subscribe', methods=['GET', 'POSt'])
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        send_subscribe_mail('Subscribe Success!', email, name=name)
        flash('Confirmation email have been sent! Check your inbox.')
        redirect(url_for('index'))
    return render_template('subscribe.html', form=form)


@app.route('/unsubscribe')
def unsubscribe():
    flash('Want to unsubscribe? No way...')
    return redirect(url_for('subscribe'))


@app.route('/ckeditor', methods=['GET', 'POST'])
def ckeditor_email():
    form = RichTextForm()
    if form.validate_on_submit():
        to = form.to.data
        subject = form.subject.data
        content = form.content.data
        send_ckeditor_mail(subject, to, content)
        flash('邮件已直接发送给' + to + ':' + subject)
        return redirect(url_for('ckeditor_email'))
    return render_template('richtext.html', form=form)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


# handle image upload for ckeditor
@app.route('/upload-ck', methods=['POST'])
def upload_for_ckeditor():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('Image only!')
    f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))
    url = url_for('get_file', filename=f.filename, _external=True)
    print('---------------------------------')
    print('---------------------------------')
    print('---------------------------------')
    print('---------------------------------')
    print('---------------------------------')
    print('url是什么', url)
    return upload_success(url, f.filename)
