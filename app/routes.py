from flask import abort, render_template, request, url_for, flash, redirect
import sqlalchemy as sa
import json
from app import app, db
from app.forms import NewSplitForm, NewGameForm, NewSeriesForm
from app.models import Splits, Game, Score, Series
from app.scoring import collect_scores, parse_scores, calculate_all_scores
from itertools import islice

def chunked(data, size):
    it = iter(data)
    while chunk := list(islice(it, size)):
        yield chunk

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = NewSeriesForm()

    series_list = db.session.scalars(
        sa.select(Series).order_by(
            Series.date.asc()
        )
    ).all()

    if form.validate_on_submit():

        series = Series(
            date=form.date.data
        )

        db.session.add(series)
        db.session.flush()

        for i in range(1, 4):

            game = Game(
                series_id=series.id,
                game_number=i
            )

            db.session.add(game)

        db.session.commit()

        flash(
            f'Created bowling night '
            f'for {series.display_date}'
        )

        return redirect(url_for('index'))
    return render_template('index.html', title='Home', form=form, series_list=series_list)

@app.route('/betting', methods=['GET', 'POST'])
@app.route('/betting/<int:game_id>', methods=['GET', 'POST'])
def betting_page(game_id=None):
    series_list = db.session.scalars(
        sa.select(Series).order_by(Series.date.desc())
    ).all()

    game = None
    if game_id:
        game = db.session.get(Game, game_id)
        if not game:
            abort(404)

    return render_template('betting.html', game=game, series_list=series_list)

@app.route('/scoring', methods=['GET', 'POST'])
@app.route('/scoring/<int:game_id>', methods=['GET', 'POST'])
def scoring_page(game_id=None):
    series_list = db.session.scalars(
        sa.select(Series).order_by(
            Series.date.asc()
        )
    ).all()

    game = None
    totals = {}
    form_state = {}

    if game_id:

        game = db.session.get(Game, game_id)

        if not game:
            abort(404)

        if game.form_state:

            form_state = json.loads(
                game.form_state
            )

            raw_scores = collect_scores(form_state)

            parsed_scores = parse_scores(raw_scores)

            totals = calculate_all_scores(
                parsed_scores
            )

    if request.method == 'POST' and game:

        form_state = request.form.to_dict()

        raw_scores = collect_scores(request.form)

        parsed_scores = parse_scores(raw_scores)

        totals = calculate_all_scores(parsed_scores)

        game.form_state = json.dumps(form_state)

        db.session.commit()

        return redirect(url_for('scoring_page',game_id=game.id))

    return render_template('scoring.html', game=game, series_list=series_list, totals=totals, form_state=form_state)


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