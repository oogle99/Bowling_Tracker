from flask import abort, render_template, request, url_for, flash, redirect
import sqlalchemy as sa
from datetime import datetime
from app import app, db
from app.forms import NewSplitForm, NewGameForm
from app.models import Splits, Game
from app.scoring import collect_scores, parse_scores, calculate_all_scores
from itertools import islice

def chunked(data, size):
    it = iter(data)
    while chunk := list(islice(it, size)):
        yield chunk

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = NewGameForm()

    if form.validate_on_submit():
        flash('New game requested for date {}'
              .format(form.date.data)
        )

        game = Game(date=form.date.data)
        db.session.add(game)
        db.session.commit()
    return render_template('index.html', title='Home', form=form)

@app.route('/betting', methods=['GET', 'POST'])
@app.route('/betting/<date>', methods=['GET', 'POST'])
def betting_page(date=None):
    all_dates = Game.query.order_by(Game.date.asc()).all()
    
    for item in all_dates:
        item.display_date = datetime.strptime(item.date, "%Y-%m-%d").strftime("%b %d, %Y")

    game = None
    if date:
        game = db.first_or_404(sa.select(Game).where(Game.date == date))

        if not game:
            abort(404)
        else:
            game.display_date = datetime.strptime(game.date, "%Y-%m-%d").strftime("%b %d, %Y")
    return render_template('betting.html', game=game, all_dates=all_dates)

@app.route('/scoring', methods=['GET', 'POST'])
@app.route('/scoring/<date>', methods=['GET', 'POST'])
def scoring_page(date=None):
    all_dates = Game.query.order_by(Game.date.asc()).all()
    
    for item in all_dates:
        item.display_date = datetime.strptime(item.date, "%Y-%m-%d").strftime("%b %d, %Y")

    game = None
    if date:
        game = db.first_or_404(sa.select(Game).where(Game.date == date))

        if not game:
            abort(404)
        else:
            game.display_date = datetime.strptime(game.date, "%Y-%m-%d").strftime("%b %d, %Y")

    totals = None
    raw_input = {}
    if request.method == "POST":
        raw_input = request.form.to_dict()

        raw_scores = collect_scores(request.form)
        parsed_scores = parse_scores(raw_scores)
        print(parsed_scores)

        totals = calculate_all_scores(parsed_scores)
        print(totals)

    return render_template('scoring.html', game=game, all_dates=all_dates, totals=totals, form_state=raw_input)


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