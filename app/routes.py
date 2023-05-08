from flask import render_template, request, redirect, url_for, flash, jsonify, json, make_response
from sqlalchemy import func, and_, or_, not_
from app import app, db
from app.models import *
from app.forms import *
import csv
import os


def getStates():
    states = State.query.all()
    return states


def getMembers():
    return Member.query.all()


def getPayList():
    return db.session.query(Member, Payment).filter(Member.id == Payment.member_id).all()

# this method checks the singleAccount table if user entry exists


def check_record_in_account_listing(member):
    if SingleAccount.query.filter_by(member_id=member.id).count() > 0:
        total_payments = sum(m.amount for m in Payment.query.filter(
            Payment.member_id == member.id).all())

        # get the date the member joined and use that to calculate the total payable
        # by multiplying the total months from the date he joined by the monthly dues (#500)
        join_date = member.datejoined
        total_months_since_joining = (
            date.today().year - join_date.year) * 12 + (date.today().month - join_date.month)
        total_pay_from_admission_date = total_months_since_joining * monthly

        record = SingleAccount.query.filter_by(member_id=member.id).first()
        record.outstanding_bal = total_pay_from_admission_date - total_payments
        record.paid_to_date = total_payments
        # Get the sum of other payments that is not dues
        # record.others = sum(m.amount for m in Payment.query.filter(Payment.member_id == member_id, \
        #     not_(Payment.purpose.like('%dues'))).all())
        record.others = sum(m.amount for m in Payment.query.filter(Payment.member_id == member.id,
                                                                   and_(not_(Payment.purpose.like('%dues')), not_(Payment.purpose.like('%levy')))).all())

        return 1  # we are returning 1 to indicate the record exists in single account
    else:
        return 0  # 0 otherwise


descr = {'header': 'Our Lady Mother of Perpetual Help Catholic Church',
         'addy': 'Ajah Lagos State', 'sub_header': "Catholic Men Organization"}


@app.route('/')
@app.route('/index')
@app.route('/home')
def index():

    return render_template('app/index.html', descr=descr, title='Home')


@app.route('/executives')
def excos():
    excos = {
        'chair': {'fname': 'Bonny', 'lname': 'Mekwunye', 'email': 'bonny@kecamventures.org', 'phone': '080234587654', 'date_elect': '2018/09/21'},
        'vice': {'fname': 'Victore', 'lname': 'Arase', 'email': 'bonny@kecamventures.org', 'phone': '080234587654', 'date_elect': '2018/09/21'},
    }
    excos_list = {'chairman': "Bonny Mekwunye", 'vice chairman': "Victor Arase", 'secretary': "Benjamin Udeze",
                  'finance secretary': "Nwokolo Charles", 'PRO': "Uche Unigwe", 'welfare officer': "Idiagbonya Nosa",
                  'assistant secretary': "Peter Okobi", 'treasurer': "Leonard Iroh", 'provost': "Jude Nwokorie"}
    print(type(excos_list))
    return render_template('app/excos.html', excos_list=excos_list, descr=descr)


@app.route('/finance', methods=["GET", "POST"])
def account():

    # records = db.session\
    #             .query(Member)\
    #             .join(SingleAccount, Member.id == SingleAccount.member_id)\
    #             .all()
    single_acct = db.session.query(Member, SingleAccount).filter(Member.id == SingleAccount.member_id)\
                    .filter(Member.id == Payment.member_id).all()

    general_acct = GeneralAccount.query.order_by(-GeneralAccount.id).all()
    total_inflow = sum([acc.inflow for acc in general_acct])
    total_outflow = sum([acc.outflow for acc in general_acct])
    global_bal = total_inflow - total_outflow
    accts = [single_acct, general_acct,
             total_inflow, total_outflow, global_bal]

    # *****************************************************************#
    payment_form = PaymentForm()
    membas = Member.query.all()
    ans = 0

    # get the members names to populate the dropdown
    list_memba = [(m.id, m.firstname+' '+m.lastname) for m in membas]
    payment_form.name.choices.append((0, 'Select'))
    payment_form.name.choices.append((-1, 'Others'))
    payment_form.name.choices.extend(list_memba)
    payment_form.payment_mode.data
    if request.method == "POST":
        if payment_form.validate_on_submit():
            # get the member id as it is from a dropdowm and also a foreignKey
            member_id = payment_form.name.data
            amount = payment_form.amount.data
            purpose = payment_form.purpose.data
            payment_mode = payment_form.payment_mode.data
            payment_type = payment_form.payment_type.data
            # purpose = payment_form.purpose.data
            pay_date = payment_form.date_paid.data  # .strftime('%d/%m/%Y')

            if member_id == 0:
                flash("Please select member name", "warning")
                # return redirect(url_for('payment'))
            else:
                member = None
                payables = Finance_Setup.query.filter(
                    func.lower(Finance_Setup.name) == 'dues').first()
                monthly = payables.amount  # Monthly here refers to the monthly dues
                # insurance = payables.insurance  # Monthly here refers to th emonthly dues
                if member_id > 0:
                    # we are subtracting 1 because the list is zero based
                    member = membas[member_id - 1]

                # get the date the member joined and use that to calculate the total payable
                # by multiplying the total months from the date he joined by the monthly dues (#500)
                # join_date = member.datejoined
                # total_months_since_joining = (date.today().year - join_date.year) * 12 + (date.today().month - join_date.month)
                # total_pay_from_admission_date = total_months_since_joining * monthly
                # record.outstanding_bal = total_pay_from_admission_date - total_payments
                # record.paid_to_date = total_payments
                # total_payments = sum(m.amount for m in Payment.query.filter(Payment.member_id == member.id).all())
                # check if member entry is in SingleAccount table
                if member:
                    trans_descr = "{} by {}".format(
                        purpose, member.firstname+" "+member.lastname)
                else:
                    trans_descr = purpose
                if payment_type.lower() == "inflow":
                    inflow, outflow, trans_descr, trans_date = amount, 0, trans_descr, datetime.utcnow()
                else:
                    inflow, outflow, trans_descr, trans_date = 0, amount, trans_descr, datetime.utcnow()

                pay = Payment(member_id=member_id, amount=amount, purpose=purpose,
                              mode_of_payment=payment_mode, date_paid=pay_date)
                gen_acct = GeneralAccount(
                    inflow=inflow, outflow=outflow, descr=trans_descr, trans_date=trans_date)
                db.session.add(pay)
                db.session.add(gen_acct)
                db.session.commit()

                # The essence of this check is to ascertain whether the
                # record exists in singleAcct(Individual_Pay_Hist) Table.
                # This is only doen when treating a member record.
                if member:
                    ans = check_record_in_account_listing(member)
                    if ans == 0:
                        join_date = member.datejoined
                        total_months_since_joining = (
                            date.today().year - join_date.year) * 12 + (date.today().month - join_date.month)
                        total_pay_from_admission_date = total_months_since_joining * monthly
                        # record.outstanding_bal = total_pay_from_admission_date - total_payments
                        # record.paid_to_date = total_payments
                        # total_payments = sum(m.amount for m in Payment.query.filter(Payment.member_id == member.id).all())
                        annual_dues = monthly * 12
                        harvest = Payment.query.filter(
                            and_(Payment.member_id == member.id, Payment.purpose.like('Harvest%'))).first()
                        insurance = Payment.query.filter(
                            and_(Payment.member_id == member.id, Payment.purpose.like('insurance%'))).first()
                        others = sum(m.amount for m in Payment.query.filter(Payment.member_id == member.id,
                                                                            and_(not_(Payment.purpose.like('%dues')),
                                                                                 not_(
                                                                                     Payment.purpose.like('%levy')),
                                                                                 not_(Payment.purpose.like('insurance%')))).all())
                        total_payable = total_pay_from_admission_date
                        paid_to_date = sum(m.amount for m in Payment.query.filter(
                            Payment.member_id == member.id).all())
                        balance = paid_to_date - total_payable
                        harvest = 0 if harvest is None else harvest
                        insurance = 0 if insurance is None else insurance
                        pay_details = SingleAccount(member_id=member_id, monthly_dues=monthly, annual_dues=annual_dues,
                                                    harvest_levy=harvest, life_policy=insurance, others=others, total_pay=total_payable,
                                                    paid_to_date=paid_to_date, outstanding_bal=balance)

                        # if pay_details:
                        db.session.add(pay_details)
                    db.session.commit()
                # else:
                    # db.session.commit()
                flash("Post successful", "success")
                return redirect(url_for('payment'))
        else:
            flash("Not successful", "info")
        payment_list = getPayList()
        return render_template('app/accounts.html', accts=accts, payment_form=payment_form, descr=descr, members=getMembers(), payment_list=payment_list)
        # return redirect(url_for('payment'))
        # return render_template('app/payments.html', payment_form=payment_form)
        # payment_form = PaymentForm()

    if request.method == 'GET':
        payment_list = getPayList()
        # payment_list = db.session.query(Member, Payment).filter(Member.id == Payment.member_id).all()
        # .filter(Member.id == Payment.member_id).all()
        # return render_template('app/payments.html', payment_form=payment_form, descr=descr, members=getMembers(), payment_list=payment_list)
        return render_template('app/accounts.html', accts=accts, payment_form=payment_form, descr=descr, members=getMembers(), payment_list=payment_list)


@app.route('/viewmembers', methods=["GET", "POST"])
def membas():
    member_list = getMembers()  # Member.query.all()
    if request.method == 'POST':
        if request.form['btn_export'].lower() == 'export to csv':
            print('Yes. POSIT!!!')
            print(request.form['btn_export'])
            with open('member_list.csv', 'w') as mlist:
                # wr = csv.writer(list_of_members, quoting=csv.QUOTE_ALL)
                mlist.write('{},{},{}\n'.format(
                    'Full Name', 'Phone Number', 'Email'))
                for m in member_list:
                    # wr.writerow(m.firstname)
                    mlist.write('{},{},{}\n'.format(
                        m.firstname+' '+m.midname+' '+m.lastname, m.phone1, m.email))
            flash("Export successful", "success")
    else:
        print('Nope!!!')
    return render_template('app/member.html', member_list=member_list, descr=descr)


@app.route('/newmember', methods=["GET", "POST"])
def add_memba():
    states = getStates()
    form = MemberForm()
    # list_memba = [(m.id, m.firstname+' '+m.lastname) for m in membas]
    # payment_form.name.choices.append((0, 'Select'))
    # payment_form.name.choices.append((-1, 'Others'))
    # payment_form.name.choices.extend(list_memba)
    # form.state_of_origin.choices = [(st.id, st.name) for st in states]
    # form.state_of_origin.choices.insert(0, (0, 'Select'))

    form.state_of_origin.choices.append((0, 'Select'))
    form.state_of_origin.choices.extend([(st.id, st.name) for st in states])
    if request.method == 'POST':
        if form.validate_on_submit():
            fname = form.firstname.data
            lname = form.lastname.data
            mname = form.midname.data
            phone = form.phone1.data
            phone2 = form.phone2.data
            email = form.email.data
            # dob = form.dob.data  // uncomment later
            dateJoined = form.date_joined.data
            cmono = form.cmono.data
            status = form.membership_status.data
            state = form.state_of_origin.data
            country = form.nationality.data
            address = form.address.data

            add_member = Member.query.filter(
                Member.firstname.like(fname), Member.lastname.like(lname)).first()
            # add_member = Member.query.filter(
            #     Member.firstname+" "+Member.lastname == fname+" "+lname)
            print(f"Add_member: {add_member}")
            if add_member:
                flash("A member with this name {} exist".format(
                    fname+" "+lname), "danger")
                return redirect(url_for('add_memba'))
            else:
                new_entry = Member(firstname=fname, lastname=lname, midname=mname, address=address,
                                   email=email, status=status, state_of_origin=state, cmono=cmono,
                                   datejoined=dateJoined, nationality=country, phone1=phone, phone2=phone2)
                db.session.add(new_entry)
                # add_member.firstname=fname  // dob=dob,
                # add_member.lastname=lname
                # add_member.midname=mname
                # add_member.address=address
                # add_member.email=email
                # add_member.status=status
                # add_member.state_of_origin=state
                # add_member.cmono = cmono
                # add_member.dob=dob
                # add_member.datejoined=dateJoined
                # add_member.nationality=country
                # add_member.phone1=phone
                # add_member.phone2=phone2
                # db.session.add(new_entry)
                db.session.commit()
                flash("Member details saved successfully", "success")
            # return redirect(url_for('membas'))
        else:
            flash("Error inserting record", "danger")
            # return render_template('app/member_add.html',form=form, descr=descr, states=states)
            # return redirect(url_for('add_memba'))s
    return render_template('app/member_add.html', form=form, descr=descr, states=states)


@app.route('/editmember/<int:id>', methods=["GET", "POST"])
def edit_memba(id):
    states = getStates()
    form = MemberForm()
    form.state_of_origin.choices = [(st.id, st.name) for st in states]
    form.state_of_origin.choices.insert(0, (0, 'Select'))
    editMember = Member.query.get(int(id))
    if request.method == 'POST':
        fname = form.firstname.data
        lname = form.lastname.data
        mname = form.midname.data
        phone = form.phone1.data
        phone2 = form.phone2.data
        email = form.email.data
        dob = form.dob.data
        dateJoined = form.date_joined.data
        cmono = form.cmono.data
        status = form.membership_status.data
        state = form.state_of_origin.data
        country = form.nationality.data
        address = form.address.data

        print('Selected state {} {}'.format(state, 'Hello'))
        if editMember is None:
            new_entry = Member(firstname=fname, lastname=lname, midname=mname, address=address,
                               email=email, status=status, state_of_origin=state, cmono=cmono, dob=dob,
                               datejoined=dateJoined, nationality=country, phone1=phone, phone2=phone2)
            db.session.add(new_entry)
        else:
            old_joined_date = editMember.datejoined
            editMember.firstname = fname
            editMember.lastname = lname
            editMember.midname = mname
            editMember.address = address
            editMember.email = email
            editMember.status = status
            editMember.state_of_origin = state
            editMember.cmono = cmono
            editMember.dob = dob
            editMember.datejoined = dateJoined
            editMember.nationality = country
            editMember.phone1 = phone
            editMember.phone2 = phone2

            # print(old_joined_date.strftime('%d/%m/%Y'))
            # print(dateJoined.strftime('%d/%m/%Y'))
            # print(dateJoined.strftime('%d/%m/%Y') == old_joined_date.strftime('%d/%m/%Y'))

        db.session.commit()
        if old_joined_date.strftime('%d/%m/%Y') != dateJoined.strftime('%d/%m/%Y'):
            print('processing.....')
            ans = check_record_in_account_listing(editMember)
        print('Selected state {}'.format(state))
        return redirect(url_for('membas'))
    else:
        form.firstname.data = editMember.firstname
        form.lastname.data = editMember.lastname
        form.midname.data = editMember.midname
        form.phone1.data = editMember.phone1
        form.phone2.data = editMember.phone2
        form.email.data = editMember.email
        form.dob.data = editMember.dob
        form.date_joined.data = editMember.datejoined
        form.cmono.data = editMember.cmono
        form.membership_status.data = editMember.status
        form.state_of_origin.data = editMember.state_of_origin
        form.nationality.data = editMember.nationality
        form.address.data = editMember.address
    return render_template('app/member_add.html', form=form, descr=descr, states=states)


@app.route('/payment', methods=["GET", "POST"])
def payment():
    payment_form = PaymentForm()
    membas = Member.query.all()
    ans = 0

    # get the members names to populate the dropdown
    list_memba = [(m.id, m.firstname+' '+m.lastname) for m in membas]
    payment_form.name.choices.append((0, 'Select'))
    payment_form.name.choices.append((-1, 'Others'))
    payment_form.name.choices.extend(list_memba)
    payment_form.payment_mode.data
    if request.method == "POST":
        if payment_form.validate_on_submit():
            # get the member id as it is from a dropdowm and also a foreignKey
            member_id = payment_form.name.data
            amount = payment_form.amount.data
            purpose = payment_form.purpose.data
            payment_mode = payment_form.payment_mode.data
            payment_type = payment_form.payment_type.data
            # purpose = payment_form.purpose.data
            pay_date = payment_form.date_paid.data  # .strftime('%d/%m/%Y')
            # print(payment_type.lower())
            # return
            # print(type(pay_date))
            # print(pay_date.ctime())
            # print(pay_date.strftime('%b/%d/%Y'))
            # dd = pay_date.strftime('%d/%m/%Y')
            # print(dd)
            # print(datetime.strptime(dd,'%d/%m/%Y'))

            # return render_template('app/payments.html', payment_form=payment_form, descr=descr, members=getMembers(), payment_list=payment_list)
            if member_id == 0:
                flash("Please select member name", "warning")
                # return redirect(url_for('payment'))
            else:
                member = None
                payables = Finance_Setup.query.filter(
                    func.lower(Finance_Setup.name) == 'dues').first()
                monthly = payables.amount  # Monthly here refers to the monthly dues
                # insurance = payables.insurance  # Monthly here refers to th emonthly dues
                if member_id > 0:
                    # we are subtracting 1 because the list is zero based
                    member = membas[member_id - 1]

                # get the date the member joined and use that to calculate the total payable
                # by multiplying the total months from the date he joined by the monthly dues (#500)
                # join_date = member.datejoined
                # total_months_since_joining = (date.today().year - join_date.year) * 12 + (date.today().month - join_date.month)
                # total_pay_from_admission_date = total_months_since_joining * monthly
                # record.outstanding_bal = total_pay_from_admission_date - total_payments
                # record.paid_to_date = total_payments
                # total_payments = sum(m.amount for m in Payment.query.filter(Payment.member_id == member.id).all())
                # check if member entry is in SingleAccount table
                if member:
                    trans_descr = "{} by {}".format(
                        purpose, member.firstname+" "+member.lastname)
                else:
                    trans_descr = purpose
                if payment_type.lower() == "inflow":
                    inflow, outflow, trans_descr, trans_date = amount, 0, trans_descr, datetime.utcnow()
                else:
                    inflow, outflow, trans_descr, trans_date = 0, amount, trans_descr, datetime.utcnow()

                pay = Payment(member_id=member_id, amount=amount, purpose=purpose,
                              mode_of_payment=payment_mode, date_paid=pay_date)
                gen_acct = GeneralAccount(
                    inflow=inflow, outflow=outflow, descr=trans_descr, trans_date=trans_date)
                db.session.add(pay)
                db.session.add(gen_acct)
                db.session.commit()

                # The essence of this check is to ascertain whether the
                # record exists in singleAcct(Individual_Pay_Hist) Table.
                # This is only doen when treating a member record.
                if member:
                    ans = check_record_in_account_listing(member)
                    if ans == 0:
                        join_date = member.datejoined
                        total_months_since_joining = (
                            date.today().year - join_date.year) * 12 + (date.today().month - join_date.month)
                        total_pay_from_admission_date = total_months_since_joining * monthly
                        # record.outstanding_bal = total_pay_from_admission_date - total_payments
                        # record.paid_to_date = total_payments
                        # total_payments = sum(m.amount for m in Payment.query.filter(Payment.member_id == member.id).all())
                        annual_dues = monthly * 12
                        harvest = Payment.query.filter(
                            and_(Payment.member_id == member.id, Payment.purpose.like('Harvest%'))).first()
                        insurance = Payment.query.filter(
                            and_(Payment.member_id == member.id, Payment.purpose.like('insurance%'))).first()
                        others = sum(m.amount for m in Payment.query.filter(Payment.member_id == member.id,
                                                                            and_(not_(Payment.purpose.like('%dues')),
                                                                                 not_(
                                                                                     Payment.purpose.like('%levy')),
                                                                                 not_(Payment.purpose.like('insurance%')))).all())
                        total_payable = total_pay_from_admission_date
                        paid_to_date = sum(m.amount for m in Payment.query.filter(
                            Payment.member_id == member.id).all())
                        balance = paid_to_date - total_payable
                        harvest = 0 if harvest is None else harvest
                        insurance = 0 if insurance is None else insurance
                        pay_details = SingleAccount(member_id=member_id, monthly_dues=monthly, annual_dues=annual_dues,
                                                    harvest_levy=harvest, life_policy=insurance, others=others, total_pay=total_payable,
                                                    paid_to_date=paid_to_date, outstanding_bal=balance)

                        # if pay_details:
                        db.session.add(pay_details)
                    db.session.commit()
                # else:
                    # db.session.commit()
                flash("Post successful", "success")
                # return redirect(url_for('payment'))
        else:
            flash("Not successful", "info")
        payment_list = getPayList()
        return render_template('app/payments.html', payment_form=payment_form, descr=descr, members=getMembers(), payment_list=payment_list)
        # return redirect(url_for('payment'))
        # return render_template('app/payments.html', payment_form=payment_form)
        # payment_form = PaymentForm()

    if request.method == 'GET':
        payment_list = getPayList()
        # payment_list = db.session.query(Member, Payment).filter(Member.id == Payment.member_id).all()
        # .filter(Member.id == Payment.member_id).all()
        return render_template('app/payments.html', payment_form=payment_form, descr=descr, members=getMembers(), payment_list=payment_list)


@app.route('/reports', methods=["GET", "POST"])
def reports():
    pass


@app.route('/setup', methods=["GET", "POST"])
def setup():
    setup_form = FinanceSetupForm()
    return render_template('app/setup.html', setup_form=setup_form)
