from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class MemberForm(FlaskForm):
    cmono = StringField('CMO Number')
    firstname = StringField('First Name', validators=[
                            DataRequired(message="First Name is required")])
    lastname = StringField('Last Name', validators=[
                           DataRequired(message="Larst Name is required")])
    midname = StringField('Other Name')
    address = StringField('Address', validators=[
                          DataRequired(message="Address is required")])
    # gender = SelectField('Gender', validators=[DataRequired(
    #     message="Gender is required")], choices=[('M', 'Male'), ('F', 'Female')])
    dob = StringField('Month and Date of Birth', validators=[
                      DataRequired()])
    phone1 = StringField('Phone', validators=[
                         DataRequired(message="Phone is required")])
    phone2 = StringField('Other Phone')
    email = StringField('Email', validators=[
                        DataRequired(message="Email is required")])
    state_of_origin = SelectField('State of Origin', validators=[DataRequired(message="State of Origin is required")],
                                  choices=[], coerce=int)

    nationality = StringField('Nationality', validators=[
                              DataRequired(message="Nationality is required")])
    date_joined = DateField('Date Joined', validators=[DataRequired(
        message="Date Initiated is required")], format='%d/%m/%Y')
    membership_status = SelectField('Status', validators=[DataRequired(message="Status is required")],
                                    choices=[('0', 'Select'),
                                             ('Active', 'Active'),
                                             ('Inactive', 'Inactive'),
                                             ('Deceased', 'Deceased')])
    submit = SubmitField('Submit')
    # degree_in_order  = StringField('Degree', validators=[DataRequired(message="Degree is required")])
    # place_initiated = StringField('Initiated Venue', validators=[DataRequired(message="Initiated Venue is required")])
    # initiated_sc  = StringField('Initiated Sub-Council', validators=[DataRequired(message="Initiated Sub-Council is required")])
    # initiated_sc  = SelectField('Initiated Sub-Council', validators=[DataRequired()], choices=[], coerce=int)
    # current_sc = SelectField('Current Sub-Council', validators=[DataRequired()], choices=[], coerce=int)


class IndividualAccountForm(FlaskForm):
    # firstname = StringField('First Name', validators=[DataRequired(message="First Name is required")])
    # lastname = StringField('Last Name', validators=[DataRequired(message="Larst Name is required")])
    # midname = StringField('Other Name', validators=[DataRequired(message="Othername is required")])
    name = SelectField('Name', validators=[
                       DataRequired()], choices=[], coerce=int)
    monthly_dues = IntegerField(
        'Dues', validators=[DataRequired(message="Enter monthly payable")])
    harvest_dues = IntegerField(
        'Dues', validators=[DataRequired(message="Enter monthly payable")])
    annual_pay = StringField('Annual Dues', validators=[
                             DataRequired(message="Enter monthly payable")])
    submit = SubmitField('Submit')


class GeneralAccountForm(FlaskForm):
    name = SelectField('Name', validators=[
                       DataRequired()], choices=[], coerce=int)
    monthly_dues = IntegerField(
        'Dues', validators=[DataRequired(message="Enter monthly payable")])
    purpose = StringField('Purpose', validators=[
                          DataRequired(message="Description")])
    current = StringField('Balance', validators=[
                          DataRequired(message="Description")])
    last_meeting = StringField('Collection at previous meeting', validators=[
                               DataRequired(message="Description")])
    submit = SubmitField('Submit')


class PaymentForm(FlaskForm):
    name = SelectField('Name', validators=[
                       DataRequired()], choices=[], coerce=int)
    amount = IntegerField('Amount', validators=[
                          DataRequired(message="Amount paid")])
    # purpose = SelectField('Purpose', validators=[DataRequired(message="Purpose")],
    #                     choices=[('Dues', 'Dues'),
    #                             ('Harvest Levy', 'Harvest Levy'),
    #                             ('Insurance', 'Insurance'),
    #                             ('Others', 'Others')])
    purpose = StringField('Purpose', validators=[
                          DataRequired(message="Purpose")])
    payment_mode = SelectField('Mode of Payment', validators=[DataRequired(message="Status is required")],
                               choices=[('0', 'Select'),
                                        ('Cash', 'Cash'),
                                        ('Bank Deposit', 'Bank Deposit'),
                                        ('Transfer', 'Transfer')])
    payment_type = SelectField('Payment Type',
                               choices=[('0', 'Select'),
                                        ('Inflow', 'Inflow/Income'),
                                        ('Outflow', 'Outflow/Expense')])
    date_paid = DateField('Date Paid', validators=[
                          DataRequired()])  # , format='%d/%m/%Y'
    submit = SubmitField('Submit')


class FinanceSetupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="Name")])
    amount = IntegerField('Amount', validators=[
                          DataRequired(message="Enter Amount")])
    descr = StringField('Purpose', validators=[
                        DataRequired(message="Purpose")])
    enforce = BooleanField('Enforce?')
    submit = SubmitField('Submit')
    # payment_mode = StringField('Mode of Payment', validators=[DataRequired(message="Mode of Payment")])
    # payment_mode = SelectField('Mode of Payment', validators=[DataRequired(message="Status is required")],
    #                     choices=[('0', 'Select'),
    #                             ('Cash', 'Cash'),
    #                             ('Bank Deposit', 'Bank Deposit'),
    #                             ('Transfer', 'Transfer')])


class ExpenseForm(FlaskForm):
    amount = IntegerField('Amount', validators=[
                          DataRequired(message="Enter Amount")])
    descr = StringField('Purpose', validators=[
                        DataRequired(message="Purpose")])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Submit')
