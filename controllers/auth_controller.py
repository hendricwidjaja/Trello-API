from datetime import timedelta

from flask import Blueprint, request

from models.user import User, user_schema, UserSchema
from init import bcrypt, db
from utils import auth_as_admin_decorator

from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register_user():
    try:
        # Get the data from the body of the request
        body_data = UserSchema().load(request.get_json())
        # Create an instance of the User Model
        user = User(
            name = body_data.get("name"),
            email = body_data.get("email")
        )
        # Hash the password using bcrypt
        password = body_data.get("password")
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        # Add and commit to the DB
        db.session.add(user)
        db.session.commit()
        # Return acknowledgement for the successful creation of a user account
        return user_schema.dump(user), 201
    # If user creation fails, send an appropriate error response based on the type of error/violation
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The column {err.orig.diag.column_name} is required"}, 400
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            # unique violation
            return {"error": "Email address must be unique"}, 400

@auth_bp.route("/login", methods=["POST"])
def login_user():
    # Get the data from the body of the request
    body_data = request.get_json()
    # Find the user in the database with that email address
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    # If the user exists and the password is correct
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # create a JWT token
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        # Then return a response to the user with their email address, admin status and JWT token
        return {"email": user.email, "is_admin": user.is_admin, "token": token}
    # Else
    else:
        # Respond back with an error message
        return {"error": "Invalid email or password"}, 400
    
# /auth/users/
@auth_bp.route("/users/", methods=["PUT", "PATCH"])
# Check if the user has a valid JWT token in the header of their request
@jwt_required()
def update_user():
    # get the fields from the body of the request
    body_data = UserSchema().load(request.get_json(), partial=True)
    # If the user inserts a new passowrd, store the new password in a variable named "password" 
    password = body_data.get("password")
    # fetch the user from the database by extracting the user's identity from the JWT token they passed in the header and finding the user ID it matches to in the database 
    # SELECT * FROM user WHERE id = get_jwt_identity
    stmt = db.select(User).filter_by(id=get_jwt_identity())
    user = db.session.scalar(stmt)
    # if the user exists:
    if user:
        # update the fields as required
        user.name = body_data.get("name") or user.name
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        # commit the changes to the database
        db.session.commit()
        # return a response to the user, acknowledging the changes
        return user_schema.dump(user)
    # else:
    else:
        # return an error response
        return {"error": "User does not exist."}
    
# /auth/users/user_id
@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@auth_as_admin_decorator
def delete_user(user_id):
    # find the user with the id from the db
    # SELECT * FROM users WHERE id==user_id;
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    # if exists:
    if user:
        # delete the user
        db.session.delete(user)
        db.session.commit()
        # return an acknowledgement message
        return {"message": f"User with id {user_id} is deleted."}
    # else:
    else:
        # return error message
        return {"message": f"User with id {user_id} not found."}, 404