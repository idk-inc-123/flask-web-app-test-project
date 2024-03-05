from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Genres, Books
from . import db
import json
from sqlalchemy.orm import joinedload

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    try:
        books = Books.query.options(joinedload(Books.genre_rel)).all()
        genres = Genres.query.all()
        books_by_genre = {genre.name: [book for book in books if book.genre_rel == genre] for genre in genres}
        return render_template("home.html", user=current_user, books_by_genre=books_by_genre, books=books)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500

@views.route('/create-genre', methods=['GET', 'POST'])
@login_required
def create_genre():
    try:
        if request.method == 'POST':
            name = request.form.get('genre-name')
            genre = Genres.query.filter_by(name=name).first()
            if name is None or not isinstance(name, str):
                flash('Invalid name.', category='error')
            elif len(name) < 1:
                flash('Length of genre name is too short.', category='error')
            elif len(name) > 255:
                flash('Length of genre name is too long.', category='error')
            elif genre:
                flash('Genre already exists.', category='error')
            else:
                new_genre = Genres(name=name)
                db.session.add(new_genre)
                db.session.commit()
                flash('Genre created!', category='success')
        return render_template("create-genre.html", user=current_user)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500

@views.route('/create-book', methods=['GET', 'POST'])
@login_required
def create_book():
    try:
        genres = Genres.query.all()
        if request.method == 'POST':
            name = request.form.get('book-name')
            image = request.form.get('book-image')
            description = request.form.get('book-description')
            genre_id = request.form.get('genre-select')
            price = request.form.get('book-price')
            publish_date = request.form.get('book-date')
            author = request.form.get('book-author')
            stock = request.form.get('book-stock')

            existing_book = Books.query.filter_by(name=name, genre=genre_id).first()

            if not name or not image or not description or not genre_id or not price or not publish_date or not author or not stock:
                flash('Invalid form.', category='error')
            elif (len(name) < 1 or len(name) > 255) or (len(image) < 1 or len(image) > 255) or (len(author) < 1 or len(author) > 255) or (len(description) < 1 or len(description) > 500):
                flash('Invalid form.', category='error')
            elif existing_book:
                flash('Book already exists.', category='error')
            else:
                new_book = Books(name=name, image=image, description=description, genre=genre_id, author=author, publish_date=publish_date, price=price, stock=stock)
                db.session.add(new_book)
                db.session.commit()
                flash('Book created!', category='success')

        return render_template("create-book.html", user=current_user, genres=genres)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500

@views.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    try:
        book = Books.query.get(book_id)
        if not book:
            return redirect(url_for("views.home"))
        genres = Genres.query.all()
        if request.method == 'POST':
            name = request.form.get('book-name')
            image = request.form.get('book-image')
            description = request.form.get('book-description')
            genre = request.form.get('genre-select')
            price = request.form.get('book-price')
            date = request.form.get('book-date')
            author = request.form.get('book-author')
            stock = request.form.get('book-stock')

            if not name or not image or not description or not genre or not price or not date or not author or not stock:
                flash('Invalid form.', category='error')
            elif (len(name) < 1 or len(name) > 255) or (len(image) < 1 or len(image) > 255) or (len(author) < 1 or len(author) > 255) or (len(description) < 1 or len(description) > 500):
                flash('Invalid form.', category='error')
            else:
                book.name = name
                book.image = image
                book.description = description
                book.genre = genre
                book.price = price
                book.publish_date = date
                book.author = author
                book.stock = stock
                db.session.commit()
                flash('Book edited!', category='success')
                return redirect(url_for("views.home"))

        return render_template("edit-book.html", user=current_user, book=book, genres=genres)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500



@views.route('/edit-genre', methods=['GET', 'POST'])
@login_required
def edit_genre():
    genres = Genres.query.all()
    try:
        if request.method == 'POST':
            id = request.form.get('genre-select')
            name = request.form.get('genre-name')
            print(id, name)
            if not id or not name:
                flash('Invalid form.', category='error')
            elif len(name) > 255 or len(name) < 1:
                flash('Invalid form.', category='error')
            else:
                genre = Genres.query.get(id)
                genre.name = name
                db.session.commit()
                flash('Book edited!', category='success')
                return redirect(url_for("views.home"))

        return render_template("edit-genre.html", user=current_user, genres=genres)
    except Exception as e:
        return jsonify({"Error": e}), 500


@views.route('/delete-book', methods=['POST'])
@login_required
def delete_book():
    book = json.loads(request.data) 
    bookId = book['bookId']
    book = Books.query.get(bookId)
    if book:
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted!', category='success')

    return jsonify({})


@views.route('/delete-genre', methods=['POST'])
@login_required
def delete_genre():
    genre = json.loads(request.data) 
    genreId = genre['genreId']
    genre = Genres.query.get(genreId)
    if genre:
        books = Books.query.filter_by(genre=genreId).all()
        for book in books:
            db.session.delete(book)
            
        db.session.commit()
        db.session.delete(genre)
        db.session.commit()
        flash('Genre deleted!', category='success')

    return jsonify({})


@views.route('/search', methods=['POST'])
@login_required
def search():
    try:
        query = request.form.get('search')
        if query:
            books = Books.query.filter(Books.name.contains(query)).options(joinedload(Books.genre_rel)).all()
            genres = Genres.query.all()
            books_by_genre = {genre.name: [book for book in books if book.genre_rel == genre] for genre in genres}
            return render_template("home.html", user=current_user, books_by_genre=books_by_genre)
        else:
            return redirect(url_for("views.home"))
    except Exception as e:
        return jsonify({"Error": e}), 500