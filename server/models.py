from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', back_populates='planets')
    scientists = association_proxy(
        'missions',
        'scientists'
    )

    # Add serialization rules
    serialize_rules = ('-missions.planets',)


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', back_populates="scientists", cascade="all, delete-orphan")
    planets = association_proxy(
        'missions',
        'planets'
    )

    # Add serialization rules
    serialize_rules = ('-missions.scientists',)

    # Add validation
    @validates('name','field_of_study')
    def validate_fields(self, key, value):
        if not value:
            raise ValueError(f'{key} must be set')
        return value

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationships
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))

    scientists = db.relationship('Scientist', back_populates="missions")
    planets = db.relationship('Planet', back_populates="missions")

    # Add serialization rules
    serialize_rules = ('-scientists.missions','-planets.missions')

    # Add validation
    @validates('name','scientist_id','planet_id')
    def validate_fields(self, key, value):
        if not value:
            raise ValueError(f'{key} must be set')
        return value

# add any models you may need.
