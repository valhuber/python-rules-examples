import os

import sqlalchemy
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session

from python_rules.rule_bank import rule_bank_withdraw  # FIXME design why required to avoid circular imports??
from python_rules.rule_bank import rule_bank_setup
from banking.banking_logic.banking_rules_bank import activate_basic_rules

from python_rules.util import prt

'''
These listeners are part of the hand-coded logic alternative
(Not required in a rules-based approach)
'''


def before_commit(a_session: session):
    print("logic: before commit!")
    # for obj in versioned_objects(a_session.dirty):
    for obj in a_session.dirty:
        print("logic: before commit! --> " + str(obj))
        obj_class = obj.__tablename__
    print("logic called: before commit!  EXIT")


def before_flush(a_session: session, a_flush_context, an_instances):
    print("before_flush")
    for each_instance in a_session.dirty:
        print("before_flush flushing Dirty! --> " + str(each_instance))
        obj_class = each_instance.__tablename__

    for each_instance in a_session.new:
        print("before_flush flushing New! --> " + str(each_instance))
        obj_class = each_instance.__tablename__


    for each_instance in a_session.deleted:
        print("before_flush flushing New! --> " + str(each_instance))
        obj_class = each_instance.__tablename__

    print("before_flush  EXIT")


""" Initialization
1 - Connect
2 - Register listeners (either hand-coded ones above, or the logic-engine listeners).
"""

# Initialize Logging
import logging
import sys

logic_logger = logging.getLogger('logic_logger')  # for users
logic_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s - %(asctime)s - %(name)s - %(levelname)s')
handler.setFormatter(formatter)
logic_logger.addHandler(handler)

do_engine_logging = False  # TODO move to config file, reconsider level
engine_logger = logging.getLogger('engine_logger')  # for internals
if do_engine_logging:
    engine_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s - %(asctime)s - %(name)s - %(levelname)s')
    handler.setFormatter(formatter)
    engine_logger.addHandler(handler)

basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.dirname(basedir)
basedir = os.path.dirname(basedir)

conn_string = "mysql://root:espresso_logic@127.0.0.1:3309/banking"
engine = sqlalchemy.create_engine(conn_string, echo=False)  # sqlalchemy sqls...

session_maker = sqlalchemy.orm.sessionmaker()
session_maker.configure(bind=engine)
session = session_maker()

by_rules = True  # True => use rules, False => use hand code (for comparison)
rule_list = None
db = None
if by_rules:
    rule_bank_setup.setup(session, engine)
    activate_basic_rules()
    rule_bank_setup.validate(session, engine)  # checks for cycles, etc

print("\n" + prt("session created, listeners registered\n"))

