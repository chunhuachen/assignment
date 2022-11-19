from django.db import models
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__ = 'Users'
    acct = Column(String, primary_key=True)
    pwd = Column(String)
    fullname = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

'''
class DjangoUsers(models.Model):
    acct = models.CharField(max_length=64, primary_key=True)
    pwd = models.CharField(max_length=128)
    fullname = models.CharField(max_length=64)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
'''
