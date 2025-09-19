from flask import Flask, render_template, request, redirect, url_for
from library import Library, Book, AudioBook, EMagazine, LibraryException

app = Flask(__name__)
lib = Library()  # Single library instance for session


@app.route('/')
def index():
    return render_template('index.html', items=lib.items.values(), fines=lib.fines_by_user)


@app.route('/add', methods=['POST'])
def add_item():
    try:
        t = request.form.get('type')
        item_id = int(request.form.get('id'))
        title = request.form.get('title')
        author = request.form.get('author')

        if t == "book":
            pages = int(request.form.get('pages') or 0)
            lib.add_item(Book(item_id, title, author, pages))
        elif t == "audio":
            minutes = int(request.form.get('minutes') or 0)
            lib.add_item(AudioBook(item_id, title, author, minutes))
        elif t == "emag":
            issue = int(request.form.get('issue') or 0)
            lib.add_item(EMagazine(item_id, title, author, issue))

        return redirect(url_for('index'))
    except Exception as e:
        return f"<h3>Error adding item: {e}</h3>", 400


@app.route('/borrow', methods=['POST'])
def borrow_item():
    try:
        item_id = int(request.form.get('item_id'))
        user_id = int(request.form.get('user_id'))
        duration = request.form.get('duration')
        lib.borrow_item(item_id, user_id, duration)
        return redirect(url_for('index'))
    except LibraryException as e:
        return f"<h3>Error borrowing: {e}</h3>", 400


@app.route('/return', methods=['POST'])
def return_item():
    try:
        item_id = int(request.form.get('item_id'))
        lib.return_item(item_id)
        return redirect(url_for('index'))
    except LibraryException as e:
        return f"<h3>Error returning: {e}</h3>", 400


if __name__ == '__main__':
    app.run(debug=True)
