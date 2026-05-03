from flask import abort, render_template, request, url_for, flash, redirect
import sqlalchemy as sa
from datetime import datetime
from app import app, db
from app.forms import NewBettingPageForm, NewSplitForm
from app.models import Splits, Betting
from itertools import islice

def chunked(data, size):
    it = iter(data)
    while chunk := list(islice(it, size)):
        yield chunk

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    user = {'username': 'Jestin'}
    posts = [
        {
            'author': {'username': 'Rebecca'},
            'body': 'I am too confident in your coding ability!'
        },
        {
            'author': {'username': 'Jestin'},
            'body': 'I am going to fail!'
        }
    ]

    form = NewBettingPageForm()
    if form.validate_on_submit():
        flash('New betting page requested for date {}'
              .format(form.date.data)
        )
        date = Betting(date=form.date.data)
        db.session.add(date)
        db.session.commit()
        return redirect(url_for('betting_page', date=date.date))
    return render_template('index.html', title='Home', user=user, posts=posts, form=form)

@app.route('/betting')
@app.route('/betting/<date>')
def betting_page(date=None):
    all_dates = Betting.query.order_by(Betting.date.asc()).all()
    
    for item in all_dates:
        item.display_date = datetime.strptime(item.date, "%Y-%m-%d").strftime("%b %d, %Y")

    betting = None
    if date:
        betting = db.first_or_404(sa.select(Betting).where(Betting.date == date))

        if not betting:
            abort(404)
        else:
            betting.display_date = datetime.strptime(betting.date, "%Y-%m-%d").strftime("%b %d, %Y")

    return render_template('betting.html', betting=betting, all_dates=all_dates)

@app.route('/splits', methods=['GET', 'POST'])
def splits():
    all_splits = Splits.query.order_by(Splits.layout).all()
    split_groups = list(chunked(all_splits, 15))
    form = NewSplitForm()
    if form.validate_on_submit():
        flash('New split created for layout {} valued at {}'
              .format(form.layout.data, form.value.data)
              )
        split = Splits(layout=form.layout.data, value=form.value.data)
        db.session.add(split)
        db.session.commit()
        return redirect(url_for('splits'))
    return render_template('splits.html', title='Splits', form=form, split_groups=split_groups)

@app.route('/splits/delete/<int:id>', methods=['GET', 'POST'])
def delete_split(id): 
    split = Splits.query.get_or_404(id)

    if request.method == "POST":

        layout = split.layout
        value = split.value

        db.session.delete(split)
        db.session.commit()

        flash('Split {} valued at {} was deleted.'
            .format(layout, value))

        return redirect(url_for('splits'))
    return render_template('confirm_delete.html', split=split)