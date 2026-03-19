from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms import validators


class LoginForm(FlaskForm):

    email = EmailField(
        "Email",
        validators=[validators.DataRequired(), validators.Email()]
    )

    password = PasswordField(
        "Password",
        validators=[validators.DataRequired()]
    )

    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[
            validators.DataRequired(),
            validators.Length(min=4, max=25)
        ]
    )

    email = EmailField(
        "Email",
        validators=[
            validators.DataRequired(),
            validators.Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            validators.DataRequired(),
            validators.Length(min=6)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            validators.DataRequired(),
            validators.EqualTo("password", message="Passwords must match")
        ]
    )

    submit = SubmitField("Register")