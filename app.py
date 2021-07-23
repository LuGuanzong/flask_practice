from flask import Flask, url_for, redirect, session, request, make_response
import os
from jinja2.utils import generate_lorem_ipsum

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default secret')


@app.route('/')
@app.route('/hello')
def hello():
    # hello,this is a test for git.
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')
        response = '<h1>Hello, %s!</h1>' % name
        if 'logged_in' in session:
            response += '[Authenticated]'
        else:
            response += '[Not Authenticated]'
        return response


@app.route('/login/<name>')
def login(name):
    if name == 'YuqianChuishui':
        session['logged_in'] = True  # 写入session
    res = make_response(redirect(url_for('hello')))
    res.set_cookie('name', name)
    return res


@app.route('/logout')
def logout():
    if "logged_in" in session:
        session.pop('logged_in')
    return redirect(url_for('hello'))


@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)
    return '''
    <h1>A very long post</h1>
    <div class="body">%s</div>
    <button id="load">load more</button>
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script type="text/javascript">
    $(function() {
        $('#load').click(function() {
            console.log('执行了点击事件')
            $.ajax({
                url:'/more',
                type:'get',
                success:function(data){
                    $('.body').append('<p>'+data+'<p>');
                }
            })
        })
    })
    </script>
    ''' % post_body


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)


if __name__ == '__main__':
    app.run()
