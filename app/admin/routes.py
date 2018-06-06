from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.admin.forms import LanguageForm, ResultForm
from app.admin import bp
from app.models import User, Problem, Language, Result


@bp.route('/language', methods=['GET', 'POST'])
@login_required
def language():
    form = LanguageForm()
    if form.validate_on_submit():
        language = Language(
            name = form.name.data,
            compile_command = form.compile.data)
        db.session.add(language)
        db.session.commit()
        flash('Your language is now live!')
        return redirect(url_for('admin.language'))
    languages = Language.query.all()
    return render_template('admin/language.html', languages=languages, form=form)

@bp.route('/result', methods=['GET', 'POST'])
@login_required
def result():
    form = ResultForm()
    if form.validate_on_submit():
        result = Result(name = form.name.data)
        db.session.add(result)
        db.session.commit()
        flash('Your result is now live!')
        return redirect(url_for('admin.result'))
    results = Result.query.all()
    return render_template('admin/result.html', results=results, form=form)

@bp.route('/', methods=['GET'])
@login_required
def index():
    return render_template('admin/base.html')

