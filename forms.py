from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, FieldList, FormField, DateField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
import re
from datetime import date

class PhoneValidator:
    def __call__(self, form, field):
        if field.data and not re.match(r'^[0-9\-\+\(\) ]{10,15}$', field.data):
            raise ValidationError('Please enter a valid phone number.')

class ChildForm(FlaskForm):
    name = StringField('Child Name', validators=[DataRequired(), Length(min=2, max=100)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    marital_status = SelectField('Marital Status', choices=[
        ('single', 'Single'),
        ('married', 'Married'),
        ('relationship', 'In a Relationship')
    ], default='single')
    
    def validate_date_of_birth(self, field):
        if field.data > date.today():
            raise ValidationError('Date of birth cannot be in the future')

class FamilyForm(FlaskForm):
    # Head of household information
    head_name = StringField('Head of Household Name', validators=[DataRequired(), Length(min=2, max=100)])
    head_phone = StringField('Head of Household Phone', validators=[DataRequired(), PhoneValidator()])
    
    # Spouse information (optional)
    spouse_name = StringField('Spouse Name (Optional)', validators=[Optional(), Length(min=2, max=100)])
    spouse_phone = StringField('Spouse Phone (Optional)', validators=[Optional(), PhoneValidator()])
    
    # Address (optional)
    address = TextAreaField('Address (Optional)', validators=[Optional(), Length(max=500)])
    
    marital_status = SelectField('Marital Status', validators=[DataRequired()], choices=[
        ('', 'Select Status'),
        ('single', 'Single'),
        ('married', 'Married')
    ])
    
    children_count = SelectField('Number of Children', choices=[
        ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')
    ])
    
    submit = SubmitField('Save Family Information')
