from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import column_property
from sqlalchemy import and_

# The below is used when we need to use sql functions like `sum`, `average`, `min`, `max`
#  If need be, uncomment and place A) below where the operation is required with some tweeking
# from sqlalchemy.sql import func  
#  A) db.session.query(func.sum(Payment.amount).label("total")).filter(Payment.member_id==1).first()

from datetime import datetime, date
from dateutil import relativedelta

# decalring some variables used for computing the fees
annual_dues, total_pay_from_admission_date, current_balance, monthly = 0,0,0,500

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable= False)
    email = db.Column(db.String(120), index=True, unique=True, nullable= False)
    password_hash = db.Column(db.String(128), nullable = False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    # role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __repr__(self):
        return '<User: {}. Is admin: {}>'.format(self.username, self.is_admin)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, nullable=False)
    # pri

    def __repr__(self):
        return '<Role: {}>'.format(self.name)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Member(db.Model):
    __tablename__ = "members"
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(50), nullable=False, index=True)
    midname = db.Column(db.String(50), default='', index = True)
    lastname = db.Column(db.String(50), nullable=False, index = True)
    address = db.Column(db.String(150), default='')
    email = db.Column(db.String(150), default='')
    gender = db.Column(db.String(20), default='Male')
    phone1 = db.Column(db.String(20), nullable=False)
    phone2 = db.Column(db.String(20), default='')
    dob = db.Column(db.DateTime, default = datetime.utcnow)
    datejoined = db.Column(db.DateTime, default = datetime.utcnow)
    cmono = db.Column(db.String(15), default='', index = True)
    state_of_origin = db.Column(db.String(20), index = True)
    nationality = db.Column(db.String(50), default='')
    status = db.Column(db.String(50), default='')
    payments = db.relationship("Payment", backref="member", lazy=True)
    acct_summary = db.relationship("SingleAccount", backref="member", lazy=True)


def get_member_details(id):
    # id = context.get_current_parameters()['member_id']
    return Member.query.get(int(id))

def compute_payables(context):
    global annual_dues, monthly, total_pay_from_admission_date, current_balance
    id = context.get_current_parameters()['member_id']
    # member = Member.query.get(int(id))
    member = get_member_details(id)
    if member:
        join_date = member.datejoined
        total_pay_from_admission_date = (date.today().year - join_date.year) * 12 + (date.today().month - join_date.month)
     # = 500
    annual_dues = monthly * 12
    paid_to_date = sum(m.amount for m in Payment.query.filter(Payment.member_id == member_id).all())
    current_balance = total_pay_from_admission_date - paid_to_date
    return {'annual_dues':annual_dues, 'totalPay': total_pay_from_admission_date, "current_balance":current_balance}

def get_total_payable(context):
    global monthly, total_pay_from_admission_date
    total_months_active = 0
    id = context.get_current_parameters()['member_id']
    # id = context.get_current_parameters()['member_id']
    # member = Member.query.get(int(id))
    member = get_member_details(id)
    if member:
        join_date = member.datejoined
        total_months_active = (date.today().year - join_date.year) * 12 + (date.today().month - join_date.month)
        total_pay_from_admission_date = total_months_active * monthly

     # relativedelta.relativedelta(date.today(), date(2019,3,11)) 
    # (date.today().year -  date(2019,3,11).year)* 12 + (date.today().month - date(2019,3,11).month)   
     
    return (-total_pay_from_admission_date)

def get_annual_pay():
    global annual_dues, monthly
    annual_dues = monthly * 12
    return annual_dues

def calculate_balance(context):
    # to calculate balance, we get the total paid_to_date and deduct it from total_payable
    id = context.get_current_parameters()['member_id']
    member = get_member_details(id)
    
     # Payment.query.filter(Payment.purpose.like("%dues")).all()       
    # db.session.query(Member, Payment).filter(Member.id == Payment.member_id).all()
    # Method 1
    # db.session.query(func.sum(Payment.amount).label("total_paid")).filter(Payment.member_id==member_id).first()

    if member:
        member_id = member.id
        join_date = member.datejoined
        total_months_active = (date.today().year - join_date.year) * 12 + (date.today().month - join_date.month)
        total_pay_from_admission_date = total_months_active * monthly

        paid_to_date = sum(m.amount for m in Payment.query.filter(Payment.member_id == member_id).all())

        current_balance = total_pay_from_admission_date - paid_to_date

    return current_balance




def get_total_pay_todate(context):
    # to calculate balance, we get the total paid_to_date and deduct it from total_payable
    id = context.get_current_parameters()['member_id']
    member = get_member_details(id)
    member_id = member.id
     
    return sum(m.amount for m in Payment.query.filter(Payment.member_id == member_id).all())


def calculate_other_receivables(context):
    id = context.get_current_parameters()['member_id']
    member = get_member_details(id)
    member_id = member.id
    return sum(m.amount for m in Payment.query.filter(Payment.member_id == member_id, \
                        and_(~Payment.purpose.like('%dues'), ~Payment.purpose.like('%levy'))).all()) 

    

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key = True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    amount = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(100), nullable=False)
    mode_of_payment = db.Column(db.String(100), default='Cash', nullable=True)
    date_paid = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return '<Payment {}>'.format(self.member_id)
    

class SingleAccount(db.Model):
    __tablename__ = "single_account"
    id = db.Column(db.Integer, primary_key = True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    monthly_dues = db.Column(db.Integer)
    annual_dues = db.Column(db.Integer, default = get_annual_pay )  # compute_payables()['annual_dues'] 
    # Later, I will create a method called get harvest levy and get 
    # levies that will pull all records from the levy table
    harvest_levy = db.Column(db.Integer, default = 0)  
    life_policy = db.Column(db.Integer, default = 0)
    others = db.Column(db.Integer, default = 0)
    total_pay = db.Column(db.Integer, default = 0)   # compute_payables()['totalPay']
    paid_to_date = db.Column(db.Integer, default=0)
    outstanding_bal = db.Column(db.Integer, default= 0)  # compute_payables()['calculate_balance']
    remark = db.Column(db.String(100))

class GeneralAccount(db.Model):
    __tablename__ = "general_account"
    id = db.Column(db.Integer, primary_key = True)
    acct_bal = db.Column(db.Integer)
    inflow = db.Column(db.Integer, default=0)
    outflow = db.Column(db.Integer, default=0)
    descr = db.Column(db.String(120))
    trans_date = db.Column(db.DateTime, default = datetime.utcnow)
    summary = db.Column(db.Text)
    
class Executive(db.Model):
    __tablename__ = "excos"
    id = db.Column(db.Integer, primary_key = True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False, index=True)
    office = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, default = datetime.utcnow)
    end_date = db.Column(db.DateTime, default = datetime.utcnow)

class State(db.Model):
    __tablename__ = "states"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=False)

# class Levy(db.Model):
#     __tablename__ = "levies"
#     id = db.Column(db.Integer, primary_key = True)
#     name = db.Column(db.String(100))
#     levy_date = db.Column(db.DateTime, default = datetime.utcnow)
#     purpose = db.Column(db.String(30))
#     enforce = db.Column(db.Boolean, default=False, nullable=False)

class Global_Setup(db.Model):
    __tablename__ = "global_setup"
    id = db.Column(db.Integer, primary_key = True)
    organisation_name = db.Column(db.String(160))
    organisation_name2 = db.Column(db.String(160))
    organisation_address = db.Column(db.String(160))
    organisation_address2 = db.Column(db.String(160))
    organisation_phone = db.Column(db.String(160))
    organisation_email = db.Column(db.String(160))
    

class Finance_Setup(db.Model):
    __tablename__ = "finance_setup"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))
    amount = db.Column(db.Integer, default=0)
    # levy_date = db.Column(db.DateTime, default = datetime.utcnow)
    descr = db.Column(db.String(130))
    enforce = db.Column(db.Boolean, default=False, nullable=False)
    archive = db.Column(db.Boolean, default=False, nullable=False)