from . import *


class GenericForm(FlaskForm):

    def validate(self, **kwargs):
        errors = list()
        for i, j in kwargs.items():
            valid = getattr(self, "v_{}".format(i), None)
            if valid is not None:
                if not re.match(valid[0], str(j)):
                    errors.append(valid[1])
        return errors


class RegisterForm(GenericForm):
    username = StringField("Username")
    gender = SelectField("Gender", choices=[("m", "Male"), ("f", "Female"), ("t", "Trans"), ("o", "Other")])
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    birthdate = DateField('Date of Birth')
    email = StringField('Email Address')
    pwd = PasswordField('Password')
    cpwd = PasswordField('Confirm Password')

    v_username = r"^\w{4,30}$", "Username : Must be between 4-30 characters"
    v_gender = r"^[mfto]$", "Gender : Male, Female, Trans or Other"
    v_pwd = r"^(?=.*\d)(?=.*[a-zA-Z]).{8,100}$", "Password : Must be between 8-100 characters or Mix the numbers with characters!"
    v_firstname = r"^\w{,40}$", "First Name : Must not exceed 40 characters"
    v_lastname = r"^\w{,40}$", "Last Name : Must not exceed 40 characters"
    v_birthdate = r"^\d{4}[\-\/\s]?((((0[13578])|(1[02]))[\-\/\s]?(([0-2][0-9])|(3[01])))|(((0[469])|(11))[\-\/\s]?(([0-2][0-9])|(30)))|(02[\-\/\s]?[0-2][0-9]))$", "Date of Birth : Must be in this form --> DD/MM/YYYY"
    v_email = r"^[^\W][a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*\@[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*\.[a-zA-Z]{2,4}$", "Email Address : Must be in this form --> abc@example.co.za"


class LoginForm(GenericForm):
    # bio = TextAreaField()
    gender = SelectField("Gender", choices=[("m", "Male"), ("f", "Female"), ("t", "Trans"), ("o", "Other")])
    
    username = StringField("Username")
    pwd = PasswordField('Password')

    v_username = r"^\w{4,30}$", "Username does not exist, please register!"
    v_pwd = r"^(?=.*\d)(?=.*[a-zA-Z]).{8,100}$", "Password is not on the database, please reset your password!"


class ResetForm(GenericForm):
    email = StringField('Email Address')

    v_email = r"^[^\W][a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*\@[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*\.[a-zA-Z]{2,4}$",  "Email Address : Must be in this form --> abc@example.co.za"


class NewPasswordForm(GenericForm):
    pwd = PasswordField('Password')
    cpwd = PasswordField('Confirm Password')

    v_pwd = r"^(?=.*\d)(?=.*[a-zA-Z]).{8,100}$", "Password :Must be between 8-100 characters"


class profileForm(GenericForm):
    gender = SelectField("Gender", choices=[("m", "Male"), ("f", "Female"), ("t", "Trans"), ("o", "Other")])
    orientation = SelectMultipleField("Orientation", choices=[("m", "Male"), ("f", "Female"), ("t", "Trans"), ("o", "Other")])
    bio = TextAreaField("Biography")

    v_gender = r"^[mfto]$", "Gender : Male, Female, Trans or Other"
    v_orientation = r"^[mfto]+$", "Orientation : Male, Female, Trans and/or Other"


class MessageForm(GenericForm):
    message = TextAreaField("Message")


class FilterSearchForm(GenericForm):
    min_age = IntegerField("Min Age")
    max_age = IntegerField("Min Age")
    min_pop = IntegerField("Min Fame")
    max_pop = IntegerField("Max Fame")
    distance = FloatField("Distance from you")
    tags = StringField("Tags (separated by commas")
    sort = SelectField("Preferences", choices=[('age', 'Age'), ('distance', 'Distance'), ('popularity', 'Popularity'), ('s_tags', 'Tags')])
