from datetime import date, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from .extensions import db
from .forms import ActionForm, ApplicationForm
from .models import Application, STATUSES

bp = Blueprint('tracker', __name__)


def owned_application(application_id):
    return db.first_or_404(db.select(Application).where(Application.id == application_id, Application.user_id == current_user.id))


@bp.get('/')
@login_required
def dashboard():
    today = date.today()
    base = db.select(Application).where(Application.user_id == current_user.id)
    all_applications = db.session.scalars(base).all()
    counts = {status: sum(item.status == status for item in all_applications) for status in STATUSES}
    upcoming = sorted((item for item in all_applications if item.deadline and today <= item.deadline <= today + timedelta(days=7) and item.status not in ('Offered', 'Rejected')), key=lambda item: (item.deadline, item.id))
    query = request.args.get('q', '').strip()[:160]
    status = request.args.get('status', '')
    if status and status not in STATUSES:
        abort(400)
    filtered = base
    if query:
        filtered = filtered.where(or_(Application.company.contains(query, autoescape=True), Application.title.contains(query, autoescape=True)))
    if status:
        filtered = filtered.where(Application.status == status)
    applications = db.session.scalars(filtered.order_by(Application.application_date.desc(), Application.id.desc())).all()
    return render_template('dashboard.html', applications=applications, total=len(all_applications), counts=counts, upcoming=upcoming, statuses=STATUSES, query=query, selected_status=status, today=today)


@bp.route('/applications/new', methods=['GET', 'POST'])
@login_required
def create():
    form = ApplicationForm()
    if form.validate_on_submit():
        application = Application(user_id=current_user.id)
        save_fields(application, form)
        db.session.add(application)
        db.session.commit()
        flash('Application added. One step closer!', 'success')
        return redirect(url_for('tracker.detail', application_id=application.id))
    return render_template('application_form.html', form=form, editing=False)


def save_fields(application, form):
    for field in ('company', 'title', 'posting_url', 'application_date', 'deadline', 'status', 'notes'):
        setattr(application, field, getattr(form, field).data)


@bp.get('/applications/<int:application_id>')
@login_required
def detail(application_id):
    return render_template('detail.html', application=owned_application(application_id))


@bp.route('/applications/<int:application_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(application_id):
    application = owned_application(application_id)
    form = ApplicationForm(obj=application)
    if form.validate_on_submit():
        save_fields(application, form)
        db.session.commit()
        flash('Application updated.', 'success')
        return redirect(url_for('tracker.detail', application_id=application.id))
    return render_template('application_form.html', form=form, editing=True)


@bp.route('/applications/<int:application_id>/delete', methods=['GET', 'POST'])
@login_required
def delete(application_id):
    application = owned_application(application_id)
    form = ActionForm()
    if form.validate_on_submit():
        db.session.delete(application)
        db.session.commit()
        flash('Application deleted.', 'success')
        return redirect(url_for('tracker.dashboard'))
    return render_template('delete.html', application=application, form=form)
