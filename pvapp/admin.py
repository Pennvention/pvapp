from flask import session
from flask.ext.admin import AdminIndexView, expose

class MyHomeView(AdminIndexView):
    def is_accessible(self):
        if session['admin']:
            return True
        else: 
            return False
