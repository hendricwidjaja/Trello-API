from datetime import date
from flask import Blueprint
from init import db, bcrypt
from models.user import User
from models.card import Card
from models.comment import Comment

db_commands = Blueprint("db", __name__)

@db_commands.cli.command("create")
def create_tables():
    db.create_all()
    print("Tables created!")

@db_commands.cli.command("seed")
def seed_tables():
    # Create a list of User instances
    users = [
        User(
            email = "admin@email.com",
            password = bcrypt.generate_password_hash("123456").decode("utf-8"),
            is_admin = True
        ),
        User(
            name = "User A",
            email = "usera@email.com",
            password = bcrypt.generate_password_hash("123456").decode("utf-8")
        )
    ]

    db.session.add_all(users)

    cards = [
        Card(
            title = "Github Operations",
            description = "Perform mandatory github ops on the project",
            status = "To Do",
            priority = "High",
            date = date.today(),
            user = users[0]
        ), 
        Card(
            title = "Initialise the modules",
            description = "Perform init operations on the necessary modules",
            status = "Ongoing",
            priority = "High",
            date = date.today(),
            user = users[0]            
        ), 
        Card(
            title = "Add comments to the code",
            description = "Add meaningful comments where necessary",
            status = "To Do",
            priority = "Low",
            date = date.today(),
            user = users[1]
        )]

    db.session.add_all(cards)

    db.session.commit()

    print("Tables seeded!")

@db_commands.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped")