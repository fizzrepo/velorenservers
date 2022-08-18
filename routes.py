from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, current_user, logout_user, login_required, login_manager
from models import Server, User, Utility
from main import app, db, bcrypt, view_counter
import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed

# Utility.create_fake_servers(100)
"""
for user in User.query.all():
    user.set_moderator()
db.session.commit()
"""

WEBHOOK = "https://discordapp.com/api/webhooks/1001105173088845865/atkRMufln-LHqbQEgs2cc1h3kFZk3xijAd_UiGEX8iPGIKAANO8jwVeSp6jCzFthHGaO"

def send_embed_webhook(title, description, color='00ff00', image=None, thumbnail=None):
    webhook = DiscordEmbed(title=title, description=description, color=color)
    if image:
        webhook.set_image(url=image)
    if thumbnail:
        webhook.set_thumbnail(url=thumbnail)
    response = webhook.execute()
    return response

def register_server(name, description, hostname, owner, color='#ffffff', banner='default.jpg', image='default.jpg'):
    server = Server(name=name, description=description, hostname=hostname, owner=owner, colour=color, banner=banner, image=image)
    db.session.add(server)
    db.session.commit()
    return server

@app.route('/')
@view_counter.count
def index():
    page = {'title': 'Home', 'description': 'Welcome to the home page.'}
    pagination = {'page': 1, 'per_page': 10, 'next': '2', 'last':1, 'total': Server.query.count()}
    news = "We are looking for screenshots for the background of this website, please <a href='/discord'>contact us</a> if you've got any! We are also looking for moderators to review servers, if you're interested, <a href='/discord'>join the discord server</a> to apply!"
    return render_template('index.html', page=page, servers=Utility.getServers(1, 10, True), pagination=pagination, news=news), 200

@app.route('/servers/<int:page>')
@view_counter.count
def servers(page):
    if page < 1:
        return redirect(url_for('servers', page=1))
    pagemeta = {'title': 'Servers', 'description': 'List of Veloren servers.'}
    pagination = {'page': page, 'per_page': 10, 'total': Server.query.count(), 'last': page-1, 'next': page+1}
    return render_template('index.html', page=pagemeta, servers=Utility.getServers(page, 10, True), pagination=pagination), 200

@app.route('/login', methods=['GET', 'POST'])
@view_counter.count
def login():
    page = {'title': 'Login', 'description': 'Login to Veloren Servers Listing.'}
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not bcrypt.check_password_hash(user.password, password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        flash('You have been logged in!')
        return redirect(url_for('index'))
    return render_template('login.html', page=page), 200

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@view_counter.count
def register():
    page = {'title': 'Register', 'description': 'Register for Veloren Servers Listing.'}
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            confirm = request.form['confirm']
            privacy_agree = request.form['privacy_agree']
            if not privacy_agree:
                flash('You must agree to the privacy policy.')
                return redirect(url_for('register'))
            if not email:
                flash('You must enter an email address.')
                return redirect(url_for('register'))
            if password != confirm:
                flash('Passwords do not match')
                return redirect(url_for('register'))
            user = User.query.filter_by(username=username).first()
            if user is not None:
                flash('Username already taken')
                return redirect(url_for('register'))
            user = User(email=email, username=username, password=bcrypt.generate_password_hash(password), lastip=request.remote_addr, lastlogin=datetime.datetime.now())
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!')
            login_user(user)
            return redirect(url_for('index'))
        except Exception as e:
            flash('Error: have you filled in all the fields?')
            return redirect(url_for('register'))
    return render_template('register.html', page=page), 200

@app.route('/privacy')
@view_counter.count
def privacy():
    page = {'title': 'Privacy Policy', 'description': 'Privacy Policy for Veloren Servers Listing.'}
    return render_template('privacy.html', page=page), 200

@app.route('/admin')
def admin():
    views_index = view_counter.get_views('/')
    if not current_user.is_authenticated:
        flash('You must be logged in to access this page.')
        return redirect(url_for('login'))
    if not current_user.is_admin:
        flash('You are not an admin, bye.')
        return redirect(url_for('index'))
    page = {'title': 'Admin', 'description': 'Admin page for Veloren Servers Listing.'}
    return render_template('admin.html', page=page, views_index=views_index), 200

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='img/favicon.ico'))

@app.route('/discord')
@view_counter.count
def discord():
    return redirect('https://discord.gg/T56gWngbg5')
