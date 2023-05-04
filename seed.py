"""Seed database with sample data from CSV Files."""

from app import db
from models import User, Activity, Post

app.app_context().push()
# db.drop_all()
db.create_all()