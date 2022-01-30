from datetime import datetime
import secrets, os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from appData import app, db, bcrypt, mail
from appData.models import User, Post #fix import order PEP8
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

    #camelCase jest zarezerwowany dla nazw class
    def isUsernameUsed(self): #nazwa funkcji sugeruje ze sprawdzasz czy email jest uzyty, czy juz masz taki w bazie, i zwracasz False jeszeli user jest - is it ok :>?
        user = User.query.filter_by(login=self.username).first() #fajnie byloby nazywac zmienne tak samo, jak szukasz loginu to daj tam login=self.login
        if user:
            return False
        else:
            return True
    #nie musisz robic else tutaj wystarczy:
    # def is_user_name_used(self):
    #     user = User.query.filter_by(login=self.username).first()
    #     if user:
    #         return False
    #     return True

    def isEmailUsed(self): # jak wyzej 
        email = User.query.filter_by(email=self.email).first()
        if email:
            return False
        else: #else do wywalenia
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
        else: #else do wywalenia
            return False

#zamiast klasy BroccoliNewPostForm zrobilbym namedtuple
from collections import namedtuple

BroccoliNewPostForm = namedtuple(
    'BroccoliNewPostForm',
    [
        'manufacture',
        'model',
        'manufacture_year',
        'price',
        'photo',
        'description',
        'author',
        'location'
    ]
)
#uzywasz tak samo jak klasy, i mozna sie odwolywac do atrybutow jak do obiektu

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

#jak wyzej 
class BroccoliStatistics:
    def __init__(self, sumOfPosts, sumOfPostsToday, sumOfUsers, buildNumber):
        self.sumOfPosts = sumOfPosts
        self.sumOfPostsToday = sumOfPostsToday
        self.sumOfUsers = sumOfUsers
        self.buildNumber = buildNumber

# wszystko co nie jest routa wywalic do innego pliku i zaimportowac


# side routes
@app.route('/')
@app.route('/home')# okresl metody
def home():
    posts = Post.query.all()
    return render_template('index.html', title='Start', posts=posts) # nie przyjmujesz na wejsciu title,
    #ja bym go wiec nie przekazywal do render template tylko go tam wpisal na sztywno - teraz moze byc mylace


@app.route('/login')
def login():
    next_page = request.args.get('next')
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('login.html', title='Logowanie', next_page=next_page) #to samo apropo title co wyzej


@app.route('/login_proceed', methods=["POST", "GET"]) #tutaj masz dwa podejscia albo mozesz zrobic dwie routy o tej samej nazwie ale innej metodzie
#albo zrobic dwa ify i odseparowac kod ktory ma sie wykonac if request.method == get lub if request.metgond == post
def login_proceed():
    formData = BroccoliLoginForm(request.form.get('login'), request.form.get('password'),
                                 request.form.get('remember-me'))
    if formData.isUsernameUsed(): 
        user = User.query.filter_by(login=formData.username).first()
        if user.role == "Unverified":
            flash('Twoje konto nie jest zweryfikowane. Sprawdź swoją skrzynkę mailową', 'warning')
            return redirect(url_for('login'))
        elif user.role == 'Blocked': 
            # w przypadku takich stringow ja preferuje wywalenie ich na gore pliku jako globale BLOCKED = 'Blocked' i uzywanie jej wszedzie
            #idealnim rozwiazaniem byloby zrobienie tabelki w bazie user_role kolumny role i ID i sprawdzac wszedzie ID dzieku temu jak bedziesz chcial kiedys zmienic
            #nazwe roli z rasistowskiego master na main :D to zmienisz jej wartosc w kolumnie 'role' i juz kod bedzie dalej smigal (zamiast tabeli w bazie mozesz zrobic slownik
            # w osobnym pliku lub poczytac o Enumerate)
            #PRZYKLAD enuma https://docs.python.org/3/library/enum.html
            # from enum import Enum
            # class UserRole(Enum):
            #     ADMIN = 1
            #     UNVERIFIED = 2
            #     BLOCKED = 3
            
            # ur = UserRole

            # assert ur.ADMIN.value == 1
            # assert ur.UNVERIFIED.value == 2
            # assert ur.BLOCKED.value == 3
            #PRZYKLAD koniec

            flash('Twoje konto jest zablokowane. Skontaktuj się z administratorem', 'danger') 
            #kazdy string ktory jest uzywty wiecej niz raz do zmiennej na gore pliku ;) DANGER = 'danger'
            return redirect(url_for('login'))
        else:
            if user and bcrypt.check_password_hash(user.password, formData.password):
                login_user(user, remember=formData.rememberMe)
                next_page = request.form.get('next_page')
                if next_page:
                    return redirect(next_page)
                else:# else do wywalenia
                    return redirect(url_for('home'))
            else:#else do wywalenia
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
    return render_template('register.html', title='Rejestracja') # co z tym titlem ;)?


@app.route('/register_proceed', methods=["POST"])
def register_proceed():
    formData = BroccoliRegisterForm(request.form.get('login'), request.form.get('userFirstName'),
                                    request.form.get('userLastName'), request.form.get('email'),
                                    request.form.get('password'))
    if formData.isUsernameUsed():
        if formData.isEmailUsed():
            hashed_password = bcrypt.generate_password_hash(formData.password).decode('utf-8')
            verification_code = secrets.token_hex(12)
            msg = Message('Weryfikacja konta - Brokuł', sender = 'jasnycorp@gmail.com', recipients = [formData.email])
            msg.html = "Link aktywacyjny: <a href='https://"+ brocooliSecrets.appIp + "/verification_code/"+formData.username+'/'+verification_code+"'>Zweryfikuj</a>"
            mail.send(msg)
            user = User(login=formData.username, firstname=formData.firstName, lastname=formData.lastName, email=formData.email, password=hashed_password, verification_message=verification_code)
            db.session.add(user)
            # ja bym sie zastanowil czy nie napisac context managera do obslugi transakci w bazie danych, dzieki context managerowi moglbys zadbac o atomowość (atomic rule)
            # ja cos sie posypie przy commit to zawsze bedziesz mogl zrobic rollback poczytaj o tym bo to fajny wzorzec do roznych rzeczy
            # from contextlib import contextmanager
            # @contextmanager
            # def session_scope():
            #     """Provide a transactional scope around a series of operations."""
            #     session = Session()
            #     try:
            #         yield session
            #         session.commit()
            #     except:
            #         session.rollback()
            #         raise
            #     finally:
            #         session.close()
            db.session.commit()
            flash('Konto zostało utworzone! Potwierdź je korzystając z linku wysłanego na podany email.', 'info')
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
        carPhotoFile = request.files['photo'] #jezeli to jest slownik to moze sie wywalic jak nie bedzie photo w requescie
        #mozna uzyc netody .get('photo') i dac defaultowa watrosc jezeli jej nie znajdzie photo
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
def post(post_id):#nazwa metody jest troszke nie fortunna -> method POST
    post = Post.query.get_or_404(post_id)
    title = 'Ogłoszenie - ' + post.manufacture + ' ' + post.model # poczytaj o f'sting
    title = f'Ogłoszenie - {post.manufacture} {post.model}' # przyklad
    if post.author.role == "Blocked" or post.status == 'Blocked':
        flash('Ogłoszenie jest niedostępne', 'warning')
        if current_user.role != "Admin":
            return redirect(url_for('home'))
    if post.status == 'Archived':
        flash('Ogłoszenie nie jest już aktualne', 'info')
    return render_template('post.html', post=post, title=title)


@app.route('/post/<int:post_id>/edit') #metoda ;)?
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    thisYear = int(datetime.now().strftime("%Y")) #camelCase -> snake_case, wywalilbym to do osobnej metody w utils
    title = 'Edytuj ogłoszenie - ' + post.manufacture + ' ' + post.model
    if current_user.id == post.author.id or current_user.role == 'Admin':
        statuses = ['Published', 'Archived', 'Blocked'] # lista -> tupple nic z tym sie dalej nie dzieje nie musi byc mutowalne, czy te statusy moga byc inne?
        #jakbys mial je w tabelce to przy dodawaniu nowych nie musial bys tutaj dopisywac wystarczyloby na przyklad 
        #statuses = (role.role for role in Roles.query.all())
        #(unikaj zaleznosci w dol zebys nie musial poprawiac potem 100 plikow ;))
        return render_template('edit_post.html', post=post, current_year=thisYear, title=title, statuses=statuses)
    else: #else do wywalenia
        flash('Nie możesz edytować ogłoszenia które nie jest twoje!', 'warning')
        redirectLocation = '/post/' + str(post.id)
        return redirect(redirectLocation)


@app.route('/post/<int:post_id>/edit_proceed', methods=["POST"])
@login_required
def edit_proceed(post_id):
    formData = BroccoliNewPostForm(request.form.get('manufacture'), request.form.get('model'), request.form.get('manufacture_year'), request.form.get('price'), request.files['photo'], request.form.get('description'), current_user.id, request.form.get('location'))
    post = Post.query.get_or_404(post_id)
    #zrob metode w clasie Post 'edit_post' do ktorej przekazesz formData oraz request i ona zwroci ci zupdatowany post
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
    redirectLocation = '/post/' + str(post.id) # f string ;)
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
        else: #else do wywalenia
            return redirect(url_for('home'))
    else:#else do wywalenia
        flash('Nie możesz wykonać tej akcji', 'danger')
        redirectLocation = '/post/' + str(post.id)
        return redirect(redirectLocation)


@app.route('/user/<int:user_id>')
@login_required
def user(user_id):
    user = User.query.get_or_404(user_id)
    postOfUser = Post.query.filter_by(user_id=user.id).all() #nu nu nu z tym camel casem ;) co sie stanie jak odpalisz ten widok bez rekordow w bazie? jinja ogarnie fora w None ?
    title = 'Użytkownik ' + user.login
    return render_template('user.html', user=user, title=title, posts=postOfUser)


def userPasswordChnage(user_id, oldPassword, newPassword): #hm :)?
    return 'Hi'


@app.route('/user/<int:user_id>/edit')
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    title = 'Edytuj konto ' + user.login
    roles = ['User', 'Admin', 'Unverified', 'Blocked'] #to co wyzej z rolami 
    if current_user.id == user.id or current_user.role == 'Admin':
        return render_template('edit_user.html', user=user, title=title, roles=roles)
    else: #else do wywalenia
        flash('Nie możesz edytować tego konta!', 'warning')
        redirectLocation = '/user/' + str(user.id)
        return redirect(redirectLocation)


@app.route('/user/<int:user_id>/edit_proceed', methods=["POST"])
@login_required
def user_proceed(user_id):
    user = User.query.get_or_404(user_id)
    user.firstname = request.form.get('userFirstName')
    user.lastname = request.form.get('userLastName')

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
            else: #else do wywalenia
                flash('Podane obecne hasło jest niepoprawne!','warning')
                redirectLocation = '/user/' + str(user.id) + '/edit'
                return redirect(redirectLocation)
        else: #else do wywalenia
            flash('Konieczne jest podanie nowego hasła w celu jego zmiany','warning')
            redirectLocation = '/user/' + str(user.id)
            return redirect(redirectLocation)
    else:#else do wywalenia
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
    else: #elsik do wywalenia ;D
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
    else: # wisz co z tym zrobic ;D
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
    else: #ellsik a kysz
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
    else:#ellsik a kysz
        flash('Nie możesz wykonać tej czynności!', 'warning')
        return redirect(url_for(previousAction))
#musze konczyc bo zona krzyczy ;p

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
        msg = Message('Weryfikacja konta - Brokuł', sender='jasnycorp@gmail.com', recipients=[user.email])
        msg.html = "Link aktywacyjny: <a href='https://"+ brocooliSecrets.appIp + "/verification_code/" + user.login + '/' + user.verification_message + "'>Zweryfikuj</a>"
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
        msg.html = "<b>Otrzymaliśmy prośbę resetu hasła dla konta "+ user.login +" które jest skojarzone z tym adresem email</b><br><p>Jeżeli nie zgłaszałeś takiej prośby lub nie posiadasz konta na naszym portalu, poinformuj nas odpowiadając na ten adres email.</p><br><h1>Resetowanie hasła:</h1><br><p>Twoje nowe hasło: <b>"+ new_password +"</b></p><br>Kliknij w link aby przeprowadzić reset: <a href='https://"+ brocooliSecrets.appIp + "/user/"+ user.login + '/password_reset/' + verification_code + '/' + new_password +"'>https://"+ brocooliSecrets.appIp + "/user/"+ user.login + '/password_reset/' + verification_code + '/' + new_password + "</a>"
        mail.send(msg)
        flash('Polecenie zmiany hasła zostało wysłane na podany adres email.','info')
        return redirect(url_for('home'))
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
