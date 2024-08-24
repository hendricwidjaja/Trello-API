from init import db, ma
from marshmallow import fields

class Card(db.Model):
    # name of the table
    __tablename__ = "cards"

    # attributes of the table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    status = db.Column(db.String)
    priority = db.Column(db.String)
    date = db.Column(db.Date) # Created date
    # Foreign Key (users.id = tablename.primarykey attribute)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="cards")
    # deletes all associated comments on card if card is deleted
    comments = db.relationship("Comment", back_populates="cards", cascade="all, delete")


class CardSchema(ma.Schema):
    user = fields.Nested("UserSchema", only=["id", "name", "email"])
    comments = fields.List(fields.Nested("CommentSchema", exclude=["card"]))

    class Meta:
        fields = ("id", "title", "email", "description", "status", "priority", "date", "user")

card_schema = CardSchema()

cards_schema = CardSchema(many=True)