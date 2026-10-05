from datetime import date, timedelta

import click

from .extensions import db
from .models import Application, User


def register_commands(app):
    @app.cli.command('init-db')
    def init_db():
        """Create missing tables without deleting existing data."""
        db.create_all()
        click.echo('Database initialized.')

    @app.cli.command('seed-demo')
    def seed_demo():
        """Create a fictional demo account once; safe to rerun."""
        db.create_all()
        email = 'demo@jobtrack.example'
        if db.session.scalar(db.select(User).where(User.email == email)):
            click.echo('Demo account already exists; existing data left unchanged.')
            return
        user = User(email=email)
        user.set_password('DemoPass123!')
        db.session.add(user)
        db.session.flush()
        examples = [('Orbit Labs', 'Junior Python Developer', 'Interviewing', 2), ('Fern Studio', 'Backend Intern', 'Applied', 5), ('Northstar Systems', 'Flask Developer', 'Applied', 7), ('Cedar Analytics', 'Data Engineering Intern', 'Offered', 3), ('Harbor Works', 'Software Trainee', 'Rejected', None), ('Lumen Digital', 'Python Intern', 'Applied', None)]
        for index, (company, title, status, days) in enumerate(examples):
            db.session.add(Application(user_id=user.id, company=company, title=title, status=status, application_date=date.today()-timedelta(days=index+1), deadline=date.today()+timedelta(days=days) if days else None, posting_url='https://example.com/jobs', notes='Fictional demo application. Prepare portfolio and review Python fundamentals.'))
        db.session.commit()
        click.echo('Demo ready: demo@jobtrack.example / DemoPass123!')
