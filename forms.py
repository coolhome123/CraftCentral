from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FieldList, FormField, DateField
from wtforms.validators import DataRequired, Length, ValidationError
import re
from datetime import date

class PhoneValidator:
    def __call__(self, form, field):
        if not re.match(r'^[0-9\-\+\(\) ]{10,15}$', field.data):
            raise ValidationError('Please enter a valid phone number.')

class ChildForm(FlaskForm):
    name = StringField('Child Name', validators=[DataRequired(), Length(min=2, max=100)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    marital_status = SelectField('Marital Status', choices=[
        ('', 'Select Status'),
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('minor', 'Minor (Not Applicable)')
    ])
    
    def validate_date_of_birth(self, field):
        if field.data > date.today():
            raise ValidationError('Date of birth cannot be in the future')

class FamilyForm(FlaskForm):
    name = StringField('Family Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), PhoneValidator()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=5, max=500)])
    marital_status = SelectField('Marital Status', validators=[DataRequired()], choices=[
        ('', 'Select Status'),
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ])
    children_count = SelectField('Number of Children', choices=[
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')
    ])
    submit = SubmitField('Save Family Information')
