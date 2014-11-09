#! /usr/bin/env python
# -*- encoding: utf-8 -*-

# Standard Librairies
import logging
import io
from datetime import date

# Extra Librairies
from flask import Flask, request, redirect, session, url_for, \
    render_template, flash, abort, send_file, jsonify
from flask.ext.babel import gettext as _
from flask.ext.babel import Babel

# Custom Modules
from framework.all import session, SystemUser, AccountAccount, AccountMove, \
    AccountMoveLine
#from config import conf
#from auth import login, logout, requires_auth
#from sale_order import load_sale_order, delete_sale_order, \
#    currency, change_product_qty

#from erp import openerp, get_invoice_pdf, get_order_pdf, get_account_qty

# Initialization of the Apps
app = Flask(__name__)
app.secret_key = 'TACHATTE' # TODO FIXME conf.get('flask', 'secret_key')
app.debug = True
#app.debug = conf.get('flask', 'debug') == 'True'
#app.config['BABEL_DEFAULT_LOCALE'] = conf.get('localization', 'locale')
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
#    minutes=int(conf.get('auth', 'session_minute')))
babel = Babel(app)

# TODO FIXME with auth
user_id = 1

# ############################################################################
# Home Route
# ############################################################################
@app.route("/")
def home():
    return render_template(
        'home.html',
    )

@app.route("/new_expense")
def new_expense():
    expense_accounts = session.query(AccountAccount)\
        .filter_by(user_id=user_id, account_type='expense', is_quick=True)\
        .order_by(AccountAccount.code)
    print expense_accounts
    bank_accounts = session.query(AccountAccount)\
        .filter_by(user_id=user_id, account_type='bank', is_possible_to_pay=True)\
        .order_by(AccountAccount.code)
    return render_template(
        'new_expense.html',
        expense_accounts=expense_accounts,
        bank_accounts=bank_accounts,
    )

@app.route("/create_new_expense", methods=['POST'])
def create_new_expense():
    # Check args
    expense_account_id = request.form.get('expense_account', False)
    bank_account_id = request.form.get('bank_account', False)
    comment = request.form.get('comment', '')
    try:
        amount = float(request.form.get('amount', False))
    except ValueError:
        amount = 0
    if expense_account_id and bank_account_id and amount:
        expense_account = session.query(AccountAccount)\
            .filter_by(id=expense_account_id)
        bank_account = session.query(AccountAccount)\
            .filter_by(id=bank_account_id)
        toDay = date.today()
        name = _('Expense : %(name)s (%(date)s - %(comment)s)',
                name=expense_account[0].name, date=toDay, comment=comment)
        account_move = AccountMove(user_id=user_id, name=name, date=toDay)
        session.add(account_move)
        session.commit()
        expense_account_move_line = AccountMoveLine(
            move_id=account_move.id,
            name=name, debit=amount, credit=0,
            account_id=expense_account_id, date=toDay)
        session.add(expense_account_move_line)
        bank_account_move_line = AccountMoveLine(
            move_id=account_move.id,
            name=name, debit=0, credit=amount,
            account_id=bank_account_id, date=toDay)
        session.add(bank_account_move_line)
        session.commit()
        
        flash(_(
            'New Expense created successfully #%(id)d',
            id=account_move.id), 'info')
        return redirect(url_for('new_expense'))
    else:
        flash("""Error: Incorrect Arguments. """
            """expense_account_id %s ; bank_account_id %s ; amount %s""" % (
            expense_account_id, bank_account_id, amount), 'error')
        return redirect(url_for('new_expense'))

@app.route("/new_cashout")
def new_cashout():
    bank_out_accounts = session.query(AccountAccount)\
        .filter_by(user_id=user_id, account_type='bank', is_cash_out=True)\
        .order_by(AccountAccount.code)
    bank_in_accounts = session.query(AccountAccount)\
        .filter_by(user_id=user_id, account_type='bank', is_cash_in=True)\
        .order_by(AccountAccount.code)
    return render_template(
        'new_cashout.html',
        single_bank_out=len([x for x in bank_out_accounts])==1,
        single_bank_in=len([x for x in bank_in_accounts])==1,
        bank_out_accounts=bank_out_accounts,
        bank_in_accounts=bank_in_accounts,
    )

@app.route("/create_new_cashout", methods=['POST'])
def create_new_cashout():
    # Check args
    bank_in_account_id = request.form.get('bank_in_account', False)
    bank_out_account_id = request.form.get('bank_out_account', False)
    try:
        amount = float(request.form.get('amount', False))
    except ValueError:
        amount = 0
    if bank_in_account_id and bank_out_account_id and amount:
        bank_in_account = session.query(AccountAccount)\
            .filter_by(id=bank_in_account_id)
        bank_out_account = session.query(AccountAccount)\
            .filter_by(id=bank_out_account_id)
        toDay = date.today()
        name = _('Cashout : %(bank_out)s -> %(bank_in)s, (%(date)s - %(value)s)',
                bank_out=bank_out_account[0].name, date=toDay, value=amount,
                bank_in=bank_in_account[0].name)
        account_move = AccountMove(user_id=user_id, name=name, date=toDay)
        session.add(account_move)
        session.commit()
        bank_in_account_move_line = AccountMoveLine(
            move_id=account_move.id,
            name=name, debit=0, credit=amount,
            account_id=bank_in_account_id, date=toDay)
        session.add(bank_in_account_move_line)
        bank_out_account_move_line = AccountMoveLine(
            move_id=account_move.id,
            name=name, debit=amount, credit=0,
            account_id=bank_out_account_id, date=toDay)
        session.add(bank_out_account_move_line)
        session.commit()
        
        flash(_(
            'New Cashout created successfully #%(id)d - %(amount)s',
            id=account_move.id, amount=amount), 'info')
        return redirect(url_for('new_cashout'))
    else:
        flash("""Error: Incorrect Arguments. """
            """bank_in_account_id %s ; bank_out_account_id %s ; amount %s""" % (
            bank_in_account_id, bank_out_account_id, amount), 'error')
        return redirect(url_for('new_cashout'))

@app.route("/setting_account")
def setting_account():
    accounts = session.query(AccountAccount).filter_by(user_id=user_id).order_by(AccountAccount.code)
    return render_template(
        'setting_account.html',
        accounts=accounts,
    )

@app.route("/setting_user")
def setting_user():
    users = session.query(SystemUser).order_by(SystemUser.name)
    return render_template(
        'setting_user.html',
        users=users,
    )


# ############################################################################
# Technical Routes
# ############################################################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(Exception)
def error(e):
    logging.exception('an error occured')
    return render_template('error.html'), 500
