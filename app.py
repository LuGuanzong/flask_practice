from flask import Flask, render_template, flash, url_for, request, redirect, session, send_from_directory
import os
import uuid
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError
from forms import LoginForm, UploadForm, MultiUploadForm, RichTextForm, NewPostForm, SigninForm, RegisterForm, \
    SigninForm2, RegisterForm2
from flask_ckeditor import CKEditor

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default secret')  # 获取存储再环境变量中的秘钥
app.config['WTF_I18N_ENABLED'] = False  # 使修改表单校验错误提示的语言生效
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 设置请求报文的最大长度
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')  # 设置文件上传时候所保存的位置
ckeditor = CKEditor(app)  # 给CKEditor传入程序实例
app.config['CKEDITOR_SERVE_LOCAL'] = True  # flask-ckeditor会使用内置资源
app.config['CKEDITOR_HEIGHT'] = 400

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.makedirs(app.config['UPLOAD_PATH'])

app.config['ALLOWED_EXTENTSIONS'] = ['png', 'jpg', 'jpeg', 'gif']


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/html', methods=['GET', 'POST'])
def html():
    if request.method == 'POST':
        username = request.form.get('username')
        flash('Welcome home, %s!' % username)
        return redirect(url_for('index'))
    return render_template('pure_html.html')


@app.route('/basic', methods=['GET', 'POST'])
def basic():
    form = LoginForm(meta={'locales': ['zh']})
    if form.validate_on_submit():
        username = form.username.data
        flash('Welcome home, %s!' % username)
        return redirect(url_for('index'))
    print('form.username', form.username)
    return render_template('basic.html', form=form)


@app.route('/bootstrap')
def bootstrap():
    form = LoginForm()
    return render_template('bootstrap.html', form=form)


@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route('/uploaded-images')
def show_images():
    return render_template('uploaded.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENTSIONS']


def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        flash('Upload success.')
        session['filenames'] = [filename]
        return redirect(url_for('show_images'))
    return render_template('upload.html', form=form)


@app.route('/multi-upload', methods=['GET', 'POST'])
def multi_upload():
    form = MultiUploadForm()
    if request.method == 'POST':
        filenames = []
        try:
            validate_csrf(form.csrf_token.data)
        except ValidationError:
            flash('CSRF TOKEN ERROR')
            return redirect(url_for('multi_upload'))
        photos = request.files.getlist('photo')
        if not photos[0].filename:
            flash('No selected file.')
            return redirect(url_for('multi_upload'))
        for f in photos:
            if f and allowed_file(f.filename):
                filename = random_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                filenames.append(filename)
            else:
                flash('Invalid file type.')
                return redirect(url_for('multi_upload'))
        flash('Upload success.')
        session['filenames'] = filenames
        return redirect(url_for('show_images'))
    return render_template('upload.html', form=form)


@app.route('/two-submits', methods=['GET', 'POST'])
def two_submits():
    form = NewPostForm()
    if form.validate_on_submit():
        if form.save.data:
            flash('You click the "Save" button.')
        elif form.publish.data:
            flash('You click the "Publish" button.')
        return redirect(url_for('index'))
    return render_template('2submit.html', form=form)


@app.route('/multi-form', methods=['GET', 'POST'])
def multi_form():
    signin_form = SigninForm()
    register_form = RegisterForm()

    if signin_form.submit1.data and signin_form.validate():
        username = signin_form.username.data
        flash('%s, you just submit the Signin Form.' % username)
        return redirect(url_for('index'))

    if register_form.submit2.data and register_form.validate():
        username = register_form.username.data
        flash('%s, you just submit the Register Form.' % username)
        return redirect(url_for('index'))

    return render_template('2form.html', signin_form=signin_form, register_form=register_form)


@app.route('/multi-form-multi-view')
def multi_form_multi_view():
    signin_form = SigninForm2()
    register_form = RegisterForm2()
    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)


@app.route('/handle-signin', methods=['POST'])
def handle_signin():
    signin_form = SigninForm2()
    register_form = RegisterForm2()

    if signin_form.validate_on_submit():
        username = signin_form.username.data
        flash('%s, you just submit the Sigin Form.' % username)
        return redirect(url_for('index'))

    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)


@app.route('/handle-register', methods=['POST'])
def handle_register():
    signin_form = SigninForm2()
    register_form = RegisterForm2()

    if register_form.validate_on_submit():
        username = register_form.username.data
        flash('%s, you just submit the Register Form.' % username)
        return redirect(url_for('index'))

    return render_template('2form2view.html', signin_form=signin_form, register_form=register_form)


@app.route('/ckeditor', methods=['GET', 'POST'])
def integerate_ckeditor():
    form = RichTextForm()
    print('form.title', form.title)
    # if form.validate_on_submit():
    #     title = form.title.data
    #     body = form.body.data
    #     flash('Your post is published!')
    #     return render_template('post.html', title=title, body=body)
    return render_template('ckeditor.html', form=form)


if __name__ == '__main__':
    app.run()
