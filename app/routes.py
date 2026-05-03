from flask import abort, render_template, request, url_for, flash, redirect
import sqlalchemy as sa
from datetime import datetime
from app import app, db
from app.forms import NewBettingPageForm, NewSplitForm, NewScoringPageForm
from app.models import Splits, Betting, Scoring
from app.scoring import collect_scores, parse_scores, calculate_all_scores
from itertools import islice

def chunked(data, size):
    it = iter(data)
    while chunk := list(islice(it, size)):
        yield chunk

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    betting_form = NewBettingPageForm()
    scoring_form = NewScoringPageForm()

    if betting_form.validate_on_submit() and betting_form.betting_submit.data:
        flash('New betting page requested for date {}'
              .format(betting_form.date.data)
        )
        betting_date = Betting(date=betting_form.date.data)
        db.session.add(betting_date)
        db.session.commit()
        return redirect(url_for('betting_page', betting_date=betting_date.date))
    
    elif scoring_form.validate_on_submit() and scoring_form.scoring_submit.data:
        flash('New scoring page requested for date {}'
              .format(scoring_form.date.data)
        )
        scoring_date = Scoring(date=scoring_form.date.data)
        db.session.add(scoring_date)
        db.session.commit()
        return redirect(url_for('scoring_page', scoring_date=scoring_date.date))
    return render_template('index.html', title='Home', betting_form=betting_form, scoring_form=scoring_form)

@app.route('/betting', methods=['GET', 'POST'])
@app.route('/betting/<date>', methods=['GET', 'POST'])
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

@app.route('/scoring', methods=['GET', 'POST'])
@app.route('/scoring/<date>', methods=['GET', 'POST'])
def scoring_page(date=None):
    all_dates = Scoring.query.order_by(Scoring.date.asc()).all()
    
    for item in all_dates:
        item.display_date = datetime.strptime(item.date, "%Y-%m-%d").strftime("%b %d, %Y")

    scoring = None
    if date:
        scoring = db.first_or_404(sa.select(Scoring).where(Scoring.date == date))

        if not scoring:
            abort(404)
        else:
            scoring.display_date = datetime.strptime(scoring.date, "%Y-%m-%d").strftime("%b %d, %Y")

    totals = None
    raw_input = {}
    if request.method == "POST":
        raw_input = request.form.to_dict()

        raw_scores = collect_scores(request.form)
        parsed_scores = parse_scores(raw_scores)
        print(parsed_scores)

        totals = calculate_all_scores(parsed_scores)
        print(totals)

    return render_template('scoring.html', scoring=scoring, all_dates=all_dates, totals=totals, form_state=raw_input)


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