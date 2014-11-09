#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, Date, Float
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

#import logging

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)


# #############################################################################
# SytemUser Class
# #############################################################################
class SystemUser(Base):
    __tablename__ = 'system_user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<SystemUser(#=%s, name='%s', email='%s')>" % (self.id, self.name, self.email)

# #############################################################################
# AccountAccount Class
# #############################################################################
class AccountAccount(Base):
    __tablename__ = 'account_account'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    parent_id = Column(Integer, ForeignKey('account_account.id'))
    user_id = Column(Integer, ForeignKey('system_user.id'))
    user = relationship('SystemUser', primaryjoin=user_id == SystemUser.id)
    parent_id = Column(Integer, ForeignKey('account_account.id'))
    parent = relationship('AccountAccount', remote_side=[id])
    type = Column(Enum('normal', 'view', name='type'))
    account_type = Column(Enum('expense', 'profit', 'bank', 'third_party', name='account_type'))
    is_quick = Column(Boolean, default=False)
    is_possible_to_pay = Column(Boolean, default=False)
    is_cash_in = Column(Boolean, default=False)
    is_cash_out = Column(Boolean, default=False)

    def __repr__(self):
        return "<AccountAccount(#=%s, code='%s', name='%s')>" % (self.id, self.code, self.name)


# #############################################################################
# AccountMove Class
# #############################################################################
class AccountMove(Base):
    __tablename__ = 'account_move'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('system_user.id'))
    user = relationship('SystemUser', primaryjoin=user_id == SystemUser.id)
    name = Column(String)
    date = Column(Date)

    def __repr__(self):
        return "<AccountMove(#=%s, name='%s')>" % (self.id, self.code, self.name)


# #############################################################################
# AccountMoveLine Class
# #############################################################################
class AccountMoveLine(Base):
    __tablename__ = 'account_move_line'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    move_id = Column(Integer, ForeignKey('account_move.id'))
    move = relationship('AccountMove', primaryjoin=move_id == AccountMove.id)
    account_id = Column(Integer, ForeignKey('account_account.id'))
    account = relationship('AccountAccount', primaryjoin=account_id == AccountAccount.id)
    debit = Column(Float)
    credit = Column(Float)
    date = Column(Date)

    def __repr__(self):
        return "<AccountMoveLine(#=%s)>" % (self.id)


# #############################################################################
# Engine Process
# #############################################################################
engine = create_engine("postgresql://legalsylvain:legalsylvain@localhost:5432/legalsylvain")
Session = sessionmaker(bind=engine)
session = Session()


# #############################################################################
# Populate Process
# #############################################################################
if False:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Populate SystemUser
    user = SystemUser(
        name='Sylvain LE GAL', email='legalsylvain@gmail.com',
        password='password')
    session.add(user)
    session.commit()

    # Populate Expense AccountAccount
    account_expense = AccountAccount(
        user_id=user.id, code='6x', name='Charge', type='view',
        account_type='expense',)
    session.add(account_expense)
    session.commit()

    account_appartment = AccountAccount(
        user_id=user.id, code='6x1', name='Appartement', type='view',
        account_type='expense', parent_id=account_expense.id)
    session.add(account_appartment)

    session.commit()
    account_rental = AccountAccount(
        user_id=user.id, code='6x11', name='Loyer', type='normal',
        account_type='expense', parent_id=account_appartment.id)
    session.add(account_rental)
    session.commit()

    account_gaz = AccountAccount(
        user_id=user.id, code='6x12', name='Gaz', type='normal',
        account_type='expense', parent_id=account_appartment.id)
    session.add(account_gaz)
    session.commit()

    account_chill_out = AccountAccount(
        user_id=user.id, code='6x2', name='Sortie', type='view',
        account_type='expense', parent_id=account_expense.id)
    session.add(account_chill_out)

    session.commit()
    account_bar = AccountAccount(
        user_id=user.id, code='6x21', name='Bar', type='normal',
        account_type='expense', parent_id=account_chill_out.id, is_quick=True)
    session.add(account_bar)
    session.commit()

    account_tabacco = AccountAccount(
        user_id=user.id, code='6x22', name='Tabac', type='normal',
        account_type='expense', parent_id=account_chill_out.id, is_quick=True)
    session.add(account_tabacco)
    session.commit()

    # Populate Bank AccountAccount
    account_bank = AccountAccount(
        user_id=user.id, code='5x', name='Banque', type='view',
        account_type='bank')
    session.add(account_bank)
    session.commit()
    account_money = AccountAccount(
        user_id=user.id, code='5x1', name='Liquide', type='normal',
        account_type='bank', parent_id=account_bank.id,
        is_possible_to_pay=True, is_cash_in=True)
    session.add(account_money)
    account_coop = AccountAccount(
        user_id=user.id, code='5x2', name='Credit Coop / Cheque', type='normal',
        account_type='bank', parent_id=account_bank.id,
        is_possible_to_pay=True, is_cash_out=True)
    session.add(account_coop)
    session.commit()
