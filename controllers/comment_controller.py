from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.comment import Comment, comment_schema, comments_schema
from models.card import Card

comments_bp = Blueprint("comments", __name__, url_prefix="/<int:card_id>/comments")

# /card_id/comments/ - GET - no need to define as users will never want/receive all comments that exist. only for comments for a specific card

# Create comment route
@comments_bp.route("/", methods=["POST"])
@jwt_required()
def create_comment(card_id):
    # get the comment message from the request body
    body_data = request.get_json()
    # fetch the card with id=card_id
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    # if card exists:
    if card:
        # create an instance of the comment model
        comment = Comment(
            message = body_data.get("message"),
            date = date.today(),
            card = card,
            user_id = get_jwt_identity()
        )
        # add and commit the session
        db.session.add(comment)
        db.session.commit()
        # return acknowledgement 
        return comment_schema.dump(comment), 201
    # else
    else:
        # return error
        return {"error": f"Card with id {card_id} not found"}
    
# Delete Comment - /cards/<int:card_id>/comments/comment_id
@comments_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(card_id, comment_id):
    # fetch comment from the db where id=comment_id
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)
    # if exists:
    if comment:
        # delete
        db.session.delete(comment)
        db.session.commit()
        # return acknowledgement message
        return {"message": f"Comment '{comment.message}' deleted successfully."}
    # else:
    else:
        # return error message
        return {"error": f"Comment with id {comment_id} not found"}, 404
    
# Update comment: /cards/card_id/comments/comment_id
@comments_bp.route("/<int:comment_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_comment(card_id, comment_id):
    # get the value from the body of the request
    body_data = request.get_json()
    # fetch the comment from the db where id=comment_id
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)
    # if exists:
    if comment:
        # update the entry
        comment.message = body_data.get("message") or comment.message
        # commit to the DB
        db.session.commit()
        # return the updated comment
        return comment_schema.dump(comment)
    # else
    else:
        # return an error message
        return {"error": f"Comment with id {comment_id} not found."}, 404