from app import db
from app.models import Participant
from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField
from wtforms.validators import Email, DataRequired, ValidationError

class EmailForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        participant = db.session.execute(db.select(Participant).filter_by(email=email.data)).first()

        if participant == None:
            raise ValidationError("Email not found. Please use a Registered Email Address.")
