from datetime import datetime
import secrets, os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from appData import app, db, bcrypt, mail
from appData.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from appData import brocooliSecrets


class BroccoliRegisterForm:
    def __init__(self, username, firstName, lastName, email, password):
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password

    def isUsernameUsed(self):
        user = User.query.filter_by(login=self.username).first()
        if user:
            return False
        else:
            return True

    def isEmailUsed(self):
        email = User.query.filter_by(email=self.email).first()
        if email:
            return False
        else:
            return True


class BroccoliLoginForm:
    def __init__(self, username, password, rememberMe):
        self.username = username
        self.password = password
        self.rememberMe = rememberMe

    def isUsernameUsed(self):
        user = User.query.filter_by(login=self.username).first()
        if user:
            return True
        else:
            return False


class BroccoliNewPostForm:
    def __init__(self, manufacture, model, manufacture_year, price, photo, description, author,
                 location):  # author = user_id
        self.manufacture = manufacture
        self.model = model
        self.manufacture_year = manufacture_year
        self.price = price
        self.photo = photo
        self.description = description
        self.author = author
        self.location = location


class BroccoliStatistics:
    def __init__(self, sumOfPosts, sumOfPostsToday, sumOfUsers, buildNumber):
        self.sumOfPosts = sumOfPosts
        self.sumOfPostsToday = sumOfPostsToday
        self.sumOfUsers = sumOfUsers
        self.buildNumber = buildNumber


# side routes
@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    return render_template('index.html', title='Start', posts=posts)


@app.route('/login')
def login():
    next_page = request.args.get('next')
    print(next_page)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('login.html', title='Logowanie', next_page=next_page)


@app.route('/login_proceed', methods=["POST", "GET"])
def login_proceed():
    formData = BroccoliLoginForm(request.form.get('login'), request.form.get('password'),
                                 request.form.get('remember-me'))
    if formData.isUsernameUsed():
        user = User.query.filter_by(login=formData.username).first()
        if user.role == "Unverified":
            flash('Twoje konto nie jest zweryfikowane. Sprawdź swoją skrzynkę mailową', 'warning')
            return redirect(url_for('login'))
        elif user.role == 'Blocked':
            flash('Twoje konto jest zablokowane. Skontaktuj się z administratorem', 'danger')
            return redirect(url_for('login'))
        else:
            if user and bcrypt.check_password_hash(user.password, formData.password):
                login_user(user, remember=formData.rememberMe)
                next_page = request.form.get('next_page')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('home'))
            else:
                flash('Błędny login lub hasło.', 'danger')
                return redirect(url_for('login'))
    flash('Konto o podanym loginie nie istnieje. Spróbuj inny login lub zarejestruj konto', 'danger')
    return redirect(url_for('login'))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('register.html', title='Rejestracja')


@app.route('/register_proceed', methods=["POST"])
def register_proceed():
    formData = BroccoliRegisterForm(request.form.get('login'), request.form.get('userFirstName'),
                                    request.form.get('userLastName'), request.form.get('email'),
                                    request.form.get('password'))
    if formData.isUsernameUsed():
        if formData.isEmailUsed():
            hashed_password = bcrypt.generate_password_hash(formData.password).decode('utf-8')
            verification_code = secrets.token_hex(12)
            msg = Message('Weryfikacja konta - Brokół', sender = 'jasnycorp@gmail.com', recipients = [formData.email])
            msg.html = "Link aktywacyjny: <a href='http://"+ brocooliSecrets.appIp + ":2000/verification_code/"+formData.username+'/'+verification_code+"'>Zweryfikuj</a>"
            mail.send(msg)
            user = User(login=formData.username, firstname=formData.firstName, lastname=formData.lastName, email=formData.email, password=hashed_password, verification_message=verification_code)
            db.session.add(user)
            db.session.commit()
            flash('Konto zostało utworzone! Możesz się teraz zalogować.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Istnieje już konto z podanym adresem email.', 'danger')
            return redirect(url_for('login'))
    else:
        flash('Użytkownik o podanym loginie już istnieje. Wybierz inny login.', 'danger')
        return redirect(url_for('register'))


@app.route('/about')
def about():
    return render_template('about.html', title='O projekcie')


@app.route('/terms')
def terms():
    return render_template('terms.html', title='Regulamin')


@app.route('/post/new_post')
@login_required
def new_post():
    thisYear = int(datetime.now().strftime("%Y"))
    return render_template('new_post.html', title='Dodaj ogłoszenie', current_year=thisYear)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/photos', picture_fn)

    output_size = (850, 450)  # maximum image size on page
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/post/new_post_publish', methods=["POST"])
@login_required
def new_post_publish():
    formData = BroccoliNewPostForm(request.form.get('manufacture'), request.form.get('model'),
                                   request.form.get('manufacture_year'), request.form.get('price'),
                                   request.files['photo'], request.form.get('description'), current_user.id,
                                   request.form.get('location'))
    if formData.photo:
        carPhotoFile = request.files['photo']
        carPhoto = save_picture(carPhotoFile)
        post = Post(user_id=formData.author, manufacture=formData.manufacture, model=formData.model,
                    manufacture_year=formData.manufacture_year, photo=carPhoto, description=formData.description,
                    price=formData.price, location=formData.location)
    else:
        post = Post(user_id=formData.author, manufacture=formData.manufacture, model=formData.model,
                    manufacture_year=formData.manufacture_year, description=formData.description, price=formData.price,
                    location=formData.location)
    db.session.add(post)
    db.session.commit()
    flash('Utworzono nowe głoszenie !', 'success')
    return redirect(url_for('home'))


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    title = 'Ogłoszenie - ' + post.manufacture + ' ' + post.model
    if post.author.role == "Blocked" or post.status == 'Blocked':
        flash('Ogłoszenie jest niedostępne', 'warning')
        if current_user.role != "Admin":
            return redirect(url_for('home'))
    if post.status == 'Archived':
        flash('Ogłoszenie nie jest już aktualne', 'info')
    return render_template('post.html', post=post, title=title)


@app.route('/post/<int:post_id>/edit')
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    thisYear = int(datetime.now().strftime("%Y"))
    title = 'Edytuj ogłoszenie - ' + post.manufacture + ' ' + post.model
    if current_user.id == post.author.id or current_user.role == 'Admin':
        statuses = ['Published', 'Archived', 'Blocked']
        return render_template('edit_post.html', post=post, current_year=thisYear, title=title, statuses=statuses)
    else:
        flash('Nie możesz edytować ogłoszenia które nie jest twoje!', 'warning')
        redirectLocation = '/post/' + str(post.id)
        return redirect(redirectLocation)


@app.route('/post/<int:post_id>/edit_proceed', methods=["POST"])
@login_required
def edit_proceed(post_id):
    formData = BroccoliNewPostForm(request.form.get('manufacture'), request.form.get('model'), request.form.get('manufacture_year'), request.form.get('price'), request.files['photo'], request.form.get('description'), current_user.id, request.form.get('location'))
    post = Post.query.get_or_404(post_id)
    post.manufacture = formData.manufacture
    post.model = formData.model
    post.manufacture_year = formData.manufacture_year
    post.price = formData.price
    post.location = formData.location
    post.description = formData.description
    post.date_posted = datetime.utcnow()
    if formData.photo:
        newPhoto = request.files['photo']
        post.photo = save_picture(newPhoto)
    if request.form.get('status'):
        post.status = request.form.get('status')
    db.session.commit()
    redirectLocation = '/post/' + str(post.id)
    return redirect(redirectLocation)


@app.route('/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.id == post.author.id or current_user.role == 'Admin':
        if post.photo != 'defaultCar.jpg':
            os.remove(os.path.join(app.root_path, 'static/photos', post.photo))
        db.session.query(Post).filter(Post.id == post.id).delete()
        db.session.commit()
        flash('Ogłoszenie zostało usunięte', 'success')
        if request.args.get('back'):
            return redirect(url_for(request.args.get('back')))
        else:
            return redirect(url_for('home'))
    else:
        flash('Nie możesz wykonać tej akcji', 'danger')
        redirectLocation = '/post/' + str(post.id)
        return redirect(redirectLocation)


@app.route('/user/<int:user_id>')
@login_required
def user(user_id):
    user = User.query.get_or_404(user_id)
    postOfUser = Post.query.filter_by(user_id=user.id).all()
    title = 'Użytkownik ' + user.login
    return render_template('user.html', user=user, title=title, posts=postOfUser)


def userPasswordChnage(user_id, oldPassword, newPassword):
    return 'Hi'


@app.route('/user/<int:user_id>/edit')
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    title = 'Edytuj konto ' + user.login
    roles = ['User', 'Admin', 'Unverified', 'Blocked']
    if current_user.id == user.id or current_user.role == 'Admin':
        return render_template('edit_user.html', user=user, title=title, roles=roles)
    else:
        flash('Nie możesz edytować tego konta!', 'warning')
        redirectLocation = '/user/' + str(user.id)
        return redirect(redirectLocation)


@app.route('/user/<int:user_id>/edit_proceed', methods=["POST"])
@login_required
def user_proceed(user_id):
    user = User.query.get_or_404(user_id)
    user.login = request.form.get('login')
    user.firstname = request.form.get('userFirstName')
    user.lastname = request.form.get('userLastName')
    user.email = request.form.get('email')

    if request.form.get('status'):
        user.role = request.form.get('status')

    if request.form.get('oldPassword'):
        if request.form.get('newPassword'):
            if bcrypt.check_password_hash(user.password, request.form.get('oldPassword')):
                new_password_hased = bcrypt.generate_password_hash(request.form.get('newPassword')).decode('utf-8')
                user.password = new_password_hased
                flash('Hasło zostało zmienione','info')
                db.session.commit()
                redirectLocation = '/user/' + str(user.id)
                return redirect(redirectLocation)
            else:
                flash('Podane obecne hasło jest niepoprawne!','warning')
                redirectLocation = '/user/' + str(user.id) + '/edit'
                return redirect(redirectLocation)
        else:
            flash('Konieczne jest podanie nowego hasła w celu jego zmiany','warning')
            redirectLocation = '/user/' + str(user.id)
            return redirect(redirectLocation)
    else:
        db.session.commit()
        redirectLocation = '/user/' + str(user.id)
        return redirect(redirectLocation)


@app.route('/user/<int:user_id>/delete')
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.id == user.id or current_user.role == 'Admin':
        db.session.query(User).filter(User.id == user.id).delete()
        db.session.commit()
        flash('Konto zostało usunięte', 'success')
        if request.args.get('back'):
            return redirect(url_for(request.args.get('back')))
        else:
            return redirect(url_for('home'))
    else:
        flash('Nie możesz wykonać tej akcji', 'danger')
        redirectLocation = '/user/' + str(user.id)
        return redirect(redirectLocation)


@app.route('/admin_panel')
@login_required
def admin_panel():
    if current_user.role == 'Admin':
        users = User.query.all()
        posts = Post.query.all()
        statistics = BroccoliStatistics(len(posts), len(posts), len(users),
                                        brocooliSecrets.appVersion)  # TODO separate posts created today #BUILD NUM HERE
        return render_template('admin_panel.html', title='Panel administratora', users=users, posts=posts,
                               statistics=statistics)
    else:
        flash('Nie jesteś administratorem!', 'warning')
        return redirect(url_for('home'))


@app.route('/post/<int:post_id>/delete/action_confirm', methods=["GET"])
@login_required
def post_delete_action_confirm(post_id):
    post = Post.query.get_or_404(post_id)
    nextAction = '/post/' + str(post.id) + '/delete'
    previousAction = request.args.get('back')
    if current_user.id == post.author.id or current_user.role == 'Admin':
        return render_template('action_confirm.html', nextAction=nextAction, previousAction=previousAction,
                               title='Potwierdź usunięcie ogłoszenia')
    else:
        flash('Nie możesz wykonać tej czynności!', 'warning')
        return redirect(url_for(previousAction))


@app.route('/user/<int:user_id>/delete/action_confirm', methods=["GET"])
@login_required
def user_delete_action_confirm(user_id):
    user = User.query.get_or_404(user_id)
    nextAction = '/user/' + str(user.id) + '/delete'
    previousAction = request.args.get('back')
    if current_user.id == user.id or current_user.role == 'Admin':
        return render_template('action_confirm.html', nextAction=nextAction, previousAction=previousAction,
                               title='Potwierdź usunięcie urzytkownika')
    else:
        flash('Nie możesz wykonać tej czynności!', 'warning')
        return redirect(url_for(previousAction))


@app.route('/post/<int:post_id>/archive')
@login_required
def post_archive(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.id == post.author.id or current_user.role == 'Admin':
        post.status = 'Archived'
        db.session.commit()
        flash('Ogłoszenie zostało zarchiwizowane','success')
        return redirect(url_for('home'))
    else:
        flash('Nie masz dostępu do tej opcji','warning')
        rediectLocation = '/post/'+str(post.id)
        return redirect(rediectLocation)

@app.route('/verification_code/<username>/<verification_code>')
def verify_user(username,verification_code):
    user = User.query.filter_by(login = username).first()
    if user.verification_message == verification_code and user.role == 'Unverified':
        user.role = 'User'
        db.session.commit()
        flash('Konto zostało zweryfikowane', 'success')
        return redirect(url_for('login'))
    else:
        flash('Nie można wykonac tej akcji', 'warning')
        return redirect(url_for('home'))

@app.route('/user/<int:user_id>/resend_verification')
@login_required
def resend_verification(user_id):
    if current_user.role == 'Admin':
        user = User.query.get_or_404(user_id)
        msg = Message('Weryfikacja konta - Brokół', sender='jasnycorp@gmail.com', recipients=[user.email])
        msg.html = "Link aktywacyjny: <a href='http://"+ brocooliSecrets.appIp +":2000/verification_code/" + user.login + '/' + user.verification_message + "'>Zweryfikuj</a>"
        mail.send(msg)
        flash('Wiadomość weryfikacyjna została wysłana', 'info')
        return redirect(url_for('admin_panel'))
    flash('Nie można wykonac tej akcji', 'warning')
    return redirect(url_for('home'))

@app.route('/reset_password')
def reset_password():
    return render_template('reset_password.html', title='Resetowanie hasła')

@app.route('/reset_password_proceed', methods=['POST'])
def reset_password_proceed():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        verification_code = secrets.token_hex(12)
        new_password = secrets.token_hex(4)
        user.verification_message = verification_code
        db.session.commit()
        msg = Message('Reset hasła do konta - PROJEKT BROKÓŁ', sender='jasnycorp@gmail.com', recipients=[user.email])
        msg.html = "<b>Otrzymaliśmy prośbę resetu hasła dla konta "+ user.login +" które jest skojarzone z tym adresem email</b><br><p>Jeżeli nie zgłaszałeś takiej prośby lub nie posiadasz konta na naszym portalu, poinformuj nas odpowiadając na ten adres email.</p><br><h1>Resetowanie hasła:</h1><br><p>Twoje nowe hasło: <b>"+ new_password +"</b></p><br>Kliknij w link aby przeprowadzić reset: <a href='http://"+ brocooliSecrets.appIp + ":2000/user/"+ user.login + '/password_reset/' + verification_code + '/' + new_password +"'>https://"+ brocooliSecrets.appIp + ":2000/user/"+ user.login + '/password_reset/' + verification_code + '/' + new_password + "</a>"
        mail.send(msg)
        flash('Polecenie zmiany hasła zostało wysłane na podany adres email.','info')
        return redirect(url_for('home')) #TODO check if working
    flash('Nie znaleziono kona o podanym adresie email','warning')
    return redirect(url_for('reset_password'))

@app.route('/user/<username>/password_reset/<verification_code>/<new_password>')
def password_reset_confirm(username,verification_code,new_password):
    user = User.query.filter_by(login=username).first()
    new_password_hased = bcrypt.generate_password_hash(new_password).decode('utf-8')
    if user and user.verification_message == verification_code:
        user.password = new_password_hased
        db.session.commit()
        flash('Hasło zostało zmienione na wskazane w mailu','success')
        return redirect(url_for('login'))
    flash('Nie można wykonac tej akcji', 'warning')
    return redirect(url_for('home'))

@app.route('/post/<int:post_id>/publish')
@login_required
def post_publish(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.id == post.author.id or current_user.role == 'Admin' and post.status == 'Archived':
        post.status = 'Published'
        db.session.commit()
        flash('Ogłoszenie zostało opublikowane','success')
        rediectLocation = '/post/'+str(post.id)
        return redirect(rediectLocation)
    else:
        flash('Nie masz dostępu do tej opcji','warning')
        rediectLocation = '/user/'+str(post.author.id)
        return redirect(rediectLocation)