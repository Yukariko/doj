from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.models import User, Problem, Submit, Result
from app.problem.forms import CreateProblemForm, SubmitForm
from app.problem import bp

@bp.route('/<int:problem_id>', methods=['GET'])
def problem(problem_id):
    problem = Problem.query.get(int(problem_id))
    return render_template('problem/problem.html', problem=problem)

@bp.route('/', methods=['GET'])
def problem_list():
    problems = Problem.query.all()
    return render_template('problem/problem_list.html', problems=problems)

@bp.route('/status', methods=['GET'])
def status():
    submits = Submit.query.all()
    return render_template('problem/status.html', submits=submits)


@bp.route('/submit/<int:problem_id>', methods=['GET', 'POST'])
@login_required
def submit(problem_id):
    form = SubmitForm()
    if form.validate_on_submit():
        submit = Submit(
            problem_id = problem_id,
            submitor = current_user,
            result_id = Result.query.filter_by(name="Waiting").first().id,
            language_id = form.language.data.id,
        )
        db.session.add(submit)
        db.session.commit()
        flash('Your submit is now live!')
        return redirect(url_for('problem.status'))
    problem = Problem.query.get(int(problem_id))
    return render_template('problem/submit.html', problem=problem, form=form)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_problem():
    form = CreateProblemForm()
    if form.validate_on_submit():
        problem = Problem(
            title = form.title.data,
            body = form.body.data,
            time_limit = form.time_limit.data,
            memory_limit = form.memory_limit.data,
            author = current_user)
        db.session.add(problem)
        db.session.commit()
        flash('Your problem is now live!')
        return redirect(url_for('problem.problem', problem_id = problem.id))
    return render_template('problem/create.html', form=form)