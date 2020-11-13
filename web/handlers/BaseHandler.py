import tornado.web
from tornado.escape import json_decode, json_encode

from web.ui_methods import _checkRole

from enum import Enum
class Role(Enum):
    BASIC = 2
    DATACLERK = 4
    DATACLERK_MODIFY = 8
    PHARMA_CLIENT = 7


def allowedRole(roles = None):
    def decorator(func):
        def decorated(self, *args, **kwargs):
            user = self.get_current_user()
            print(user)
            # User is refused
            if user is None:
                self.redirect("/login")
                return None

            user_role = user["role_id"]
            has_access = False
            if _checkRole(user_role, roles) == True:
                has_access = True
            if not has_access:
                self.set_status(403)
                self._transforms = []
                self.finish()
                return None

            return func(self, *args, **kwargs)
        return decorated
    return decorator


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie(self.settings["cookie_user_session"])
        if not user or user is "":
            return None
        return json_decode(user)

    def check_xsrf_cookie(self):
        pass
    
    def set_current_user(self, user=None, remember_me=False):
        user_data = "" if not user else json_encode(user)
        user_remember = 1 if not remember_me else 365
        self.set_secure_cookie(self.settings["cookie_user_session"], 
                               user_data,
                               user_remember)