import os
import sqlalchemy
import banking.banking_logic.models as models
from banking.banking_logic import session  # opens db, activates logic listener <--


delete_deposit = session.query(models.CHECKING_TRANS).filter(models.CHECKING_TRANS.TransId == 100).delete()
print("\ndelete deposit trans, deleting: " + str(delete_deposit) + "\n\n")
session.commit()

deposit = models.CHECKING_TRANS(TransId=100,CustNum=2,AcctNum=2,DepositAmt=1000,WithdrawlAmt=0,TransDate='2020-10-01')
session.add(deposit)
session.commit()

verify_deposit = session.query(models.CHECKING_TRANS).filter(models.CHECKING_TRANS.TransId == 100).one()

print("\nverify_deposit, completed: " + str(verify_deposit) + "\n\n")