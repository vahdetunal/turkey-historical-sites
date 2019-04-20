#!/usr/bin/env python3
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class Site(Base):
    __tablename__ = 'site'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    civilization = Column(String(250))
    image = Column(String(250))
    city_id = Column(Integer, ForeignKey('city.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'civilization': self.civilization
        }


class City(Base):
    __tablename__ = 'city'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    image = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    site = relationship(Site, cascade='delete')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id
        }


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    city = relationship(City)
    site = relationship(Site)


engine = create_engine("postgres+psycopg2://postgres:postgres@localhost:5432/historicalsights2")

Base.metadata.create_all(engine)
