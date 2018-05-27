from flask import Flask
from flask import render_template, flash, redirect, url_for
from config import Config
from login import LoginForm


app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
                form.username.data, form.remember_me.data
            ))
        return redirect(url_for('index'))
    return render_template('login.html', form=form)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
