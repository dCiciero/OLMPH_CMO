from app import app, db
from app.models import *

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User':User, 'Role':Role, 'Member':Member, 'IndAcct':SingleAccount,\
        'Payment':Payment,'State':State, 'Exco':Executive, 'Finance': Finance_Setup, \
            'Global': Global_Setup, 'gen_acct':GeneralAccount}
