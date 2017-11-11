import os, sys, datetime
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    username = Column(String(80), nullable = False)
    email = Column(String(80), nullable = False)
    picture = Column(String(250))
    id = Column(Integer, primary_key = True)
    password_hash = Column(String(80))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Catalog(Base):
    __tablename__ = 'catalog'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable = True)

    @property
    def serialize(self):
        return{
            'id' : self.id,
            'name' : self.name
    }

class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable = True)
    description = Column(String(2000))
    create_date = Column(DateTime, default=datetime.datetime.now)
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id':self.id,
            'name':self.name,
            'description':self.description,
        }


engine = create_engine('sqlite:///catalogappwithuserslogin.db')
Base.metadata.create_all(engine)