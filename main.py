from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data import db_session
from data.users import User
from data.jobs import Jobs


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class JobsForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    teamlead_id = StringField("Team Leader id", validators=[DataRequired()])
    work_size = StringField("Work Size", validators=[DataRequired()])
    collaborators = StringField("Collaborators", validators=[DataRequired()])
    is_finished = BooleanField("Is job finished?")
    submit = SubmitField('Submit')


def main():
    db_session.global_init('db/jobs.sqlite')

    @login_manager.user_loader
    def load_user(user_id):
        session = db_session.create_session()
        return session.query(User).get(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    @app.route("/")
    def index():
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        users = session.query(User).all()
        names = {name.id: (name.surname, name.name) for name in users}
        return render_template("index.html", jobs=jobs, names=names)

    @app.route('/addjob', methods=['GET', 'POST'])
    @login_required
    def add_job():
        form = JobsForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            jobs = Jobs()
            jobs.job = form.title.data
            jobs.team_leader = int(form.teamlead_id.data)
            jobs.work_size = int(form.work_size.data)
            jobs.collaborators = form.collaborators.data
            jobs.is_finished = form.is_finished.data
            current_user.jobs.append(jobs)
            session.merge(current_user)
            session.commit()
            return redirect('/')
        return render_template('job.html', title='Adding a Job',
                               form=form)

    app.run()


if __name__ == '__main__':
    main()
