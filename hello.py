from flask import Flask
from flask import Flask, render_template,session, redirect, url_for,flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
#to  create database#
from flask_sqlalchemy import SQLAlchemy
#to update de basadate#
from flask_migrate import Migrate
#Flask-Mail is initialized as shown #
from flask_mail import Mail
import os
#this function can render email bodies from Jinja2 templates to have the most flexibility.#
from flask_mail import Message






#to  create database#
basedir= os.path.abspath(os.path.dirname(__file__))



class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
#configuration of database#
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
moment = Moment(app)
#configuration of database#
db = SQLAlchemy(app)
# to migrate# 
migrate = Migrate(app, db)
#Flask-Mail is initialized as shown #
mail = Mail(app)
#config de email, to send email from gmail#
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
#Integrating Emails with the Application#

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]' 
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin mypleasurehelpyou@gmail.com'
# email example#
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')



#configuration of database Role and User model definition#

class Role(db.Model):
    __tablename__ = 'roles' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    #relationships in the database models#
    users = db.relationship('User', backref='role', lazy='dynamic')
    

    def __repr__(self): 
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(64), unique=True, index=True)
    #relationships in the database models#
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self): 
        return '<User %r>' % self.username


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm() 
    if form.validate_on_submit():
        #database operation#
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            #to receive email when a user write in the formn#
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],
                           'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
            session['name'] = form.name.data
            form.name.data = ''
            return redirect(url_for('index'))
    return render_template('index.html',
            form=form, name=session.get('name'),
            known=session.get('known', False))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 
    

@app.errorhandler(500) 
def internal_server_error(e): 
    return render_template('500.html'), 500


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

#Integrating Emails with the Application#
def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=
    [to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
