from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('sign up')


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('login')


class DeliveryRange(FlaskForm):
    origin_pincode = StringField(validators=[DataRequired(), Length(min=1, max=6)])
    destination_pincode = StringField(validators=[DataRequired(), Length(min=1, max=6)])
    submit = SubmitField('Next')


class ItemDetails(FlaskForm):
    id = IntegerField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
    weight = IntegerField(validators=[DataRequired()])
    date = DateField(format='%m/%d/%Y', validators=[DataRequired()])
    receiver = StringField(validators=[DataRequired()])
    receiver_phone = StringField(validators=[DataRequired()])


class TransporterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('email', validators=[DataRequired()])
    phone_no = StringField(validators=[DataRequired()])
    vehicle_name = StringField(validators=[DataRequired()])
    vehicle_no = StringField(validators=[DataRequired()])
    driving_license = StringField(validators=[DataRequired()])


