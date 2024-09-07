from flask_jwt_extended import get_jwt_identity

from functools import wraps

from init import db
from models.user import User

'''
def authorise_as_admin():
    # get the user's id from get_jwt_identity
    user_id = get_jwt_identity()
    # fetch the user from the db
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    # check whether the user is an admin or not
    return user.is_admin

# creating a decorator for authorise_as_admin
'''
def auth_as_admin_decorator(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # get the user's id from get_jwt_identity
        user_id = get_jwt_identity()
        # fetch the user from the db
        stmt = db.select(User).filter_by(id=user_id)
        user = db.session.scalar(stmt)
        # if user is admin
        if user.is_admin:
            # allow the decorator "fn" to execute - this is because the decorator 
            return fn(*args, **kwargs)
        # else
        else:
            return {"error": "Only admin can perform this action "}, 403
        
    return wrapper