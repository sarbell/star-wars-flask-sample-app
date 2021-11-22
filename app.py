from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/{}'.format(app.root_path, 'starwars.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'b2de7FkqvkMyqzNFzxCkgnPKIGP6i4Rc'


db = SQLAlchemy(app)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)


class Trilogy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    trilogy_id = db.Column(db.Integer, db.ForeignKey('trilogy.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('Movie', lazy=True))
    trilogy = db.relationship('Trilogy', backref=db.backref('Movie', lazy=True))
    title = db.Column(db.String(100), nullable=False)
    year_made = db.Column(db.Integer, nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    poster = db.Column(db.String(100), nullable=False)


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('Series', lazy=True))
    series_title = db.Column(db.String(100), nullable=False)
    series_episode_title = db.Column(db.String(100), nullable=False)
    year_made = db.Column(db.Integer, nullable=False)
    last_year_made = db.Column(db.Integer, nullable=True)
    synopsis = db.Column(db.Text, nullable=False)
    poster = db.Column(db.String(100), nullable=False)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('Game', lazy=True))
    title = db.Column(db.String(100), nullable=False)
    gaming_system = db.Column(db.String(100), nullable=False)
    year_made = db.Column(db.Integer, nullable=False)
    synopsis = db.Column(db.Text, nullable=False)
    poster = db.Column(db.String(100), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def check_password(self, value):
        return check_password_hash(self.password, value)

db.create_all()


@app.before_request
def load_user():
    user_id = session.get('user_id')
    g.user = User.query.get(user_id) if user_id is not None else None


def login_required(f):
    @wraps(f)
    def decorated_function(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return f(**kwargs)
    return decorated_function


@app.route('/admin/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        user = User.query.filter_by(username=username).first()

        if user is None:
            error = 'Incorrect username.'
        # elif not user.check_password(password):
        #     error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('admin_authors', type='page'))

        flash(error)

    return render_template('admin/login.html')




@app.route('/')
def index():
    movies = Movie.query.all()
    series = Series.query.all()
    games = Game.query.all()
    return render_template("index.html", movies=movies, series=series, games=games)

@app.route('/movies')
def movies():
    movies = Movie.query.all()
    return render_template("movies.html", movies=movies)

@app.route('/games')
def games():
    games = Game.query.all()
    return render_template("games.html", games=games)

@app.route('/series')
def series():
    series = Series.query.all()
    return render_template("series.html", series=series)

@app.route('/feature/movie/<id>')
def feature_movies(id):
    movie = Movie.query.get_or_404(id)
    return render_template("feature.html", movie=movie)

@app.route('/feature/series/<id>')
def feature_series(id):
    serie = Series.query.get_or_404(id)
    return render_template("feature_series.html",serie=serie)


@app.route('/feature/games/<id>')
def feature_games(id):
    game = Game.query.get_or_404(id)
    return render_template("feature_game.html",game=game)




# ADMIN
@app.route('/admin/')
def admin_index():
    return render_template("admin/admin_base.html")


#### CATEGORIES
@app.route('/admin/categories')
@login_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/category.html', categories=categories)


@app.route('/admin/category/new', methods=('GET', 'POST'))
@login_required
def create_category():
    if request.method == 'POST':
        type = request.form['type']
        error = None

        if not type:
            error = 'Category name is required.'

        if error is None:
            category = Category(type=type)
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('admin_categories'))

        flash(error)

    categories = Category.query.all()
    return render_template("admin/category_form.html", categories=categories)


@app.route('/admin/category/edit/<id>', methods=('GET', 'POST'))
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)

    if request.method == 'POST':
        category.type = request.form['type']

        error = None

        if not request.form['type']:
            error = 'Category name is required.'

        if error is None:
            db.session.commit()
            return redirect(url_for('admin_categories'))

        flash(error)

    return render_template('admin/category_form.html', type=category.type)


@app.route('/admin/category/delete/<id>', methods=('GET', 'POST'))
@login_required
def delete_category(id):
    delete = True

    category = Category.query.get_or_404(id)
    error = None

    if error is None:
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('admin_categories'))

    return render_template('admin/category_form.html', category=category, delete=delete)



#### TRILOGIES
@app.route('/admin/trilogies')
@login_required
def admin_trilogies():
    trilogies = Trilogy.query.all()
    return render_template('admin/trilogy.html', trilogies=trilogies)


@app.route('/admin/trilogy/new', methods=('GET', 'POST'))
@login_required
def create_trilogy():
    if request.method == 'POST':
        type = request.form['type']
        error = None

        if not type:
            error = 'Trilogy name is required.'

        if error is None:
            trilogy = Trilogy(type=type)
            db.session.add(trilogy)
            db.session.commit()
            return redirect(url_for('admin_trilogies'))

        flash(error)

    trilogies = Trilogy.query.all()
    return render_template("admin/trilogy_form.html", trilogies=trilogies)


@app.route('/admin/trilogy/edit/<id>', methods=('GET', 'POST'))
@login_required
def edit_trilogy(id):
    trilogy = Trilogy.query.get_or_404(id)

    if request.method == 'POST':
        trilogy.type = request.form['type']

        error = None

        if not request.form['type']:
            error = 'Trilogy name is required.'

        if error is None:
            db.session.commit()
            return redirect(url_for('admin_trilogies'))

        flash(error)

    return render_template('admin/trilogy_form.html', type=trilogy.type)



@app.route('/admin/trilogy/delete/<id>', methods=('GET', 'POST'))
@login_required
def delete_trilogy(id):
    delete = True

    trilogy = Trilogy.query.get_or_404(id)
    error = None

    if error is None:
        db.session.delete(trilogy)
        db.session.commit()
        return redirect(url_for('admin_trilogies'))

    return render_template('admin/trilogy_form.html', trilogy=trilogy, delete=delete)


#### MOVIES
@app.route('/admin/movies')
@login_required
def admin_movies():
    movies = Movie.query.all()
    return render_template('admin/movies.html', movies=movies)


@app.route('/admin/movie/new', methods=('GET', 'POST'))
@login_required
def create_movie():

    categories = Category.query.all()
    trilogies = Trilogy.query.all()

    if request.method == 'POST':
        title = request.form['title']
        year_made = request.form['year_made']
        synopsis = request.form['synopsis']
        category_id = request.form['category_id']
        trilogy_id = request.form['trilogy_id']
        poster = request.form['poster']

        error = None

        if not title:
            error = 'Title is required.'

        if error is None:
            movie = Movie(title=title, year_made=year_made, synopsis=synopsis, category_id=category_id, trilogy_id=trilogy_id, poster=poster )
            db.session.add(movie)
            db.session.commit()
            return redirect(url_for('admin_movies'))

        flash(error)

    movies = Movie.query.all()
    return render_template("admin/movie_form.html", movies=movies, categories=categories, trilogies=trilogies)


@app.route('/admin/movie/edit/<id>', methods=('GET', 'POST'))
@login_required
def edit_movie(id):
    categories = Category.query.all()
    trilogies = Trilogy.query.all()
    movie = Movie.query.get_or_404(id)

    if request.method == 'POST':
        movie.title = request.form['title']
        movie.year_made = request.form['year_made']
        movie.synopsis = request.form['synopsis']
        movie.category_id = request.form['category_id']
        movie.trilogy_id = request.form['trilogy_id']
        movie.poster = request.form['poster']
        error = None

        if not request.form['title']:
            error = 'Movie name is required.'
        if error is None:
            db.session.commit()
            return redirect(url_for('admin_movies'))
        print(error)

    return render_template('admin/movie_form.html', title=movie.title, year_made=movie.year_made, synopsis=movie.synopsis, categories=categories, trilogies=trilogies, poster=movie.poster)


@app.route('/admin/movie/delete/<id>', methods=('GET', 'POST'))
@login_required
def delete_movie(id):
    delete = True

    movie = Movie.query.get_or_404(id)
    error = None

    if error is None:
        db.session.delete(movie)
        db.session.commit()
        return redirect(url_for('admin_movies'))

    return render_template('admin/movie_form.html', movie=movie, delete=delete)


#### SERIES
@app.route('/admin/series')
@login_required
def admin_series():
    series = Series.query.all()
    return render_template('admin/series.html', series=series)


@app.route('/admin/series/new', methods=('GET', 'POST'))
@login_required
def create_series():

    categories = Category.query.all()

    if request.method == 'POST':
        series_title = request.form['series_title']
        series_episode_title = request.form['series_episode_title']
        year_made = request.form['year_made']
        last_year_made = request.form['last_year_made']
        synopsis = request.form['synopsis']
        category_id = request.form['category_id']
        poster = request.form['poster']

        error = None

        if not series_title:
            error = 'Title is required.'

        if error is None:
            serie = Series(series_title=series_title, series_episode_title=series_episode_title, year_made=year_made, last_year_made=last_year_made,  synopsis=synopsis, category_id=category_id, poster=poster )
            db.session.add(serie)
            db.session.commit()
            return redirect(url_for('admin_series'))

        flash(error)

    series = Series.query.all()
    return render_template("admin/series_form.html", series=series, categories=categories)


@app.route('/admin/series/edit/<id>', methods=('GET', 'POST'))
@login_required
def edit_series(id):
    categories = Category.query.all()
    serie = Series.query.get_or_404(id)

    if request.method == 'POST':
        serie.series_title = request.form['series_title']
        serie.series_episode_title = request.form['series_episode_title']
        serie.year_made = request.form['year_made']
        serie.last_year_made = request.form['last_year_made']
        serie.synopsis = request.form['synopsis']
        serie.category_id = request.form['category_id']
        serie.poster = request.form['poster']
        error = None

        if not request.form['series_title']:
            error = 'Series name is required.'
        if error is None:
            db.session.commit()
            return redirect(url_for('admin_series'))
        print(error)

    return render_template('admin/series_form.html', series_title=serie.series_title,series_episode_title=serie.series_episode_title, year_made=serie.year_made,last_year_made=serie.last_year_made, synopsis=serie.synopsis, categories=categories, poster=serie.poster)


@app.route('/admin/series/delete/<id>', methods=('GET', 'POST'))
@login_required
def delete_series(id):
    delete = True

    serie = Series.query.get_or_404(id)
    error = None

    if error is None:
        db.session.delete(serie)
        db.session.commit()
        return redirect(url_for('admin_series'))

    return render_template('admin/series_form.html', serie=serie, delete=delete)



#### GAMES
@app.route('/admin/games')
@login_required
def admin_games():
    games = Game.query.all()
    return render_template('admin/games.html', games=games)


@app.route('/admin/games/new', methods=('GET', 'POST'))
@login_required
def create_game():

    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form['title']
        gaming_system = request.form['gaming_system']
        year_made = request.form['year_made']
        synopsis = request.form['synopsis']
        category_id = request.form['category_id']
        poster = request.form['poster']

        error = None

        if not title:
            error = 'Title is required.'

        if error is None:
            game = Game(title=title, year_made=year_made, synopsis=synopsis,gaming_system=gaming_system, category_id=category_id, poster=poster )
            db.session.add(game)
            db.session.commit()
            return redirect(url_for('admin_games'))

        flash(error)

    games = Game.query.all()
    return render_template("admin/games_form.html", games=games, categories=categories)


@app.route('/admin/games/edit/<id>', methods=('GET', 'POST'))
@login_required
def edit_game(id):
    categories = Category.query.all()
    game = Game.query.get_or_404(id)

    if request.method == 'POST':
        game.title = request.form['title']
        game.gaming_system = request.form['gaming_system']
        game.year_made = request.form['year_made']
        game.synopsis = request.form['synopsis']
        game.category_id = request.form['category_id']
        game.poster = request.form['poster']
        error = None

        if not request.form['title']:
            error = 'Game name is required.'
        if error is None:
            db.session.commit()
            return redirect(url_for('admin_games'))
        print(error)

    return render_template('admin/games_form.html', title=game.title, gaming_system=game.gaming_system, year_made=game.year_made, synopsis=game.synopsis, categories=categories, poster=game.poster)


@app.route('/admin/game/delete/<id>', methods=('GET', 'POST'))
@login_required
def delete_game(id):
    delete = True

    game = Game.query.get_or_404(id)
    error = None

    if error is None:
        db.session.delete(game)
        db.session.commit()
        return redirect(url_for('admin_games'))

    return render_template('admin/games_form.html', game=game, delete=delete)