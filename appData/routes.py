from datetime import datetime
import secrets, os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from appData import app, db, bcrypt
#from appData.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from appData.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required #copy


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
    def __init__(self, manufacture, model, manufacture_year, price, photo, description, author): #author = user_id
        self.manufacture = manufacture
        self.model = model
        self.manufacture_year = manufacture_year
        self.price = price
        self.photo = photo
        self.description = description
        self.author = author
    #TODO form validation

class BroccoliStatistics:
    def __init__(self, sumOfPosts, sumOfPostsToday, sumOfUsers, buildNumber):
        self.sumOfPosts = sumOfPosts
        self.sumOfPostsToday = sumOfPostsToday
        self.sumOfUsers = sumOfUsers
        self.buildNumber = buildNumber

#side routes
@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    return render_template('index.html', title='Start', posts = posts)


@app.route('/login')
def login():
    next_page = request.args.get('next')
    print(next_page)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('login.html', title='Logowanie', next_page=next_page)

@app.route('/login_proceed', methods=["POST","GET"])
def login_proceed():
    formData = BroccoliLoginForm(request.form.get('login'),request.form.get('password'),request.form.get('remember-me'))
    if formData.isUsernameUsed():
        user = User.query.filter_by(login=formData.username).first()
        if user and bcrypt.check_password_hash(user.password, formData.password):
            login_user(user, remember=formData.rememberMe)
            next_page = request.form.get('next_page')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            #flash(user.password,'danger')
            flash('Błędny login lub hasło.', 'danger')
            return redirect(url_for('login'))
    flash('Konto o podanym loginie nie istnieje. Spróbuj inny login lub zarejestruj konto', 'danger')
    return redirect(url_for('login')) #TODO reset password


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
    formData = BroccoliRegisterForm(request.form.get('login'),request.form.get('userFirstName'),request.form.get('userLastName'),request.form.get('email'),request.form.get('password'))
    if formData.isUsernameUsed():
        if formData.isEmailUsed():
            hashed_password = bcrypt.generate_password_hash(formData.password).decode('utf-8')
            user = User(login=formData.username, firstname=formData.firstName, lastname=formData.lastName, email=formData.email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        else:
            flash('Istnieje już konto z podanym adresem email.','danger')
            return redirect(url_for('login'))
    else:
        flash('Użytkownik o podanym loginie już istnieje. Wybierz inny login.','danger')
        return redirect(url_for('register'))


@app.route('/about')
def about():
    return render_template('about.html',title='O projekcie') #TODO


@app.route('/admin')
def admin():
    return 'Hi' #TODO


@app.route('/terms')
def terms():
    return 'Terms' #TODO


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

    output_size = (850, 450) #maximum image size on page
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/post/new_post_publish', methods=["POST"])
@login_required
def new_post_publish():
    formData = BroccoliNewPostForm(request.form.get('manufacture'),request.form.get('model'),request.form.get('manufacture_year'),request.form.get('price'),request.files['photo'],request.form.get('description'),current_user.id)
    #TODO form validation placeholder
    if formData.photo:
        carPhotoFile = request.files['photo']
        carPhoto = save_picture(carPhotoFile)
        post = Post(user_id=formData.author, manufacture=formData.manufacture, model=formData.model, manufacture_year=formData.manufacture_year, photo=carPhoto, description=formData.description, price=formData.price)
    else:
        post = Post(user_id=formData.author, manufacture=formData.manufacture, model=formData.model, manufacture_year=formData.manufacture_year, description=formData.description, price=formData.price)
    db.session.add(post)
    db.session.commit()
    flash('Utworzono nowe głoszenie !','success')
    return redirect(url_for('home'))


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    title = 'Ogłoszenie - ' + post.manufacture + ' ' + post.model
    return render_template('post.html', post=post, title=title)

@app.route('/post/<int:post_id>/edit')
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    thisYear = int(datetime.now().strftime("%Y"))
    title = 'Edytuj ogłoszenie - ' + post.manufacture + ' ' + post.model
    if current_user.id == post.author.id:
        return render_template('edit_post.html', post=post,  current_year=thisYear, title=title)
    else:
        flash('Nie możesz edytować ogłoszenia które nie jest twoje!','warning')
        redirectLocation = '/post/'+str(post.id)
        return redirect(redirectLocation)

@app.route('/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.id == post.author.id or current_user.role == 'Admin':
        if post.photo != 'defaultCar.jpg':
            os.remove(os.path.join(app.root_path, 'static/photos', post.photo))
        db.session.query(Post).filter(Post.id==post.id).delete() #TODO change parameter only
        db.session.commit()
        flash('Ogłoszenie zostało usunięte','success')
        
        if request.args.get('back'):
            return redirect(url_for(request.args.get('back')))
        else:
            return redirect(url_for('home'))
    else:
        flash('Nie możesz wykonać tej akcji','danger')
        redirectLocation = '/post/'+str(post.id)
        return redirect(redirectLocation) 


@app.route('/user/<int:user_id>')
@login_required
def user(user_id):
    user = User.query.get_or_404(user_id)
    postOfUser = Post.query.filter_by(user_id=user.id).all()
    title = 'Użytkownik '+user.login
    return render_template('user.html', user=user, title=title, posts=postOfUser)

@app.route('/user/<int:user_id>/edit')
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    title = 'Edytuj konto ' + user.login
    if current_user.id == user.id:
        return render_template('edit_user.html', user=user, title=title)
    else:
        flash('Nie możesz edytować tego konta!','warning')
        redirectLocation = '/user/'+str(user.id)
        return redirect(redirectLocation)

@app.route('/admin_panel')
@login_required
def admin_panel():
    if current_user.role == 'Admin':
        users = User.query.all()
        posts = Post.query.all()
        statistics = BroccoliStatistics(len(posts),len(posts),len(users),'0.20.2') #TODO separate posts created today #BUILD NUM HERE
        return render_template('admin_panel.html', title='Panel administratora', users=users, posts=posts, statistics=statistics)
    else:
        flash('Nie jesteś administratorem!','warning')
        return redirect(url_for('home'))

@app.route('/post/<int:post_id>/delete/action_confirm', methods=["GET"])
@login_required
def post_delete_action_confirm(post_id):
    post = Post.query.get_or_404(post_id)
    nextAction='/post/'+str(post.id)+'/delete'
    previousAction = request.args.get('back')
    if current_user.id == post.author.id or current_user.role == 'Admin':
        return render_template('action_confirm.html',nextAction=nextAction,previousAction=previousAction,title='Potwierdź usunięcie ogłoszenia')
    else:
        flash('Nie możesz wykonać tej czynności!','warning')
        return redirect(url_for(previousAction))