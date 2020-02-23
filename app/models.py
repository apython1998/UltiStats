import base64
import datetime as dt
import json
import os
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))


    def __repr__(self):
        return '<User {}>'.format(self.username)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class TournamentToPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))


class PlayerToPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    point_id = db.Column(db.Integer, db.ForeignKey('point.id'))


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    number = db.Column(db.Integer)
    position = db.Column(db.String(64))
    team_id = db.Column(
        db.Integer,
        db.ForeignKey('team.id', ondelete='SET NULL')
    )
    tournaments = db.relationship('Tournament', secondary='tournament_to_player')
    points = db.relationship('Point', secondary='player_to_point')
    statistics = db.relationship(
        'Statistic',
        backref='point',
        lazy='dynamic',
        passive_deletes=True
    )


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    players = db.relationship(
        'Player',
        backref='team',
        lazy='dynamic',
        passive_deletes=True
    )
    tournaments = db.relationship(
        'Tournament',
        backref='team',
        lazy='dynamic',
        passive_deletes=True
    )
    games = db.relationship(
        'Game',
        backref='team',
        lazy='dynamic',
        passive_deletes=True
    )



class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    start_date = db.Column(db.DateTime, default=dt.datetime.utcnow())
    end_date = db.Column(db.DateTime, default=dt.datetime.utcnow())
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    players = db.relationship('Player', secondary='tournament_to_player')
    games = db.relationship(
        'Game',
        backref='tournament',
        lazy='dynamic',
        passive_deletes=True
    )


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id'))  # Yourself
    opponent_team_name = db.Column(db.String(128))  # Name of Opponent
    points = db.relationship(
        'Point',
        backref='game',
        lazy='dynamic',
        passive_deletes=True
    )


class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    won = db.Column(db.Boolean)  # Did your team win the point?
    statistics = db.relationship(
        'Statistic',
        backref='point',
        lazy='dynamic',
        passive_deletes=True
    )
    players = db.relationship('Player', secondary='player_to_point')


class Statistic(db.Model):
    '''
    A single instance of a statistic
    i.e. a single D, a single P, a single A, a single T
    '''
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    point_id = db.Column(db.Integer, db.ForeignKey('point.id'))
    stat = db.Column(db.String)
