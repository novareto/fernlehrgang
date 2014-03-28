# -*- coding: utf-8 -*-

from . import Base
from dolmen.content import IContent
from sqlalchemy import *
from zope.interface import Interface, implementer
from zope.schema import Int, TextLine, Password


class IUser(Interface):
    
    login = TextLine(
        title=u"Login",
        required=True,
        )
    
    email = TextLine(
        title=u"Email address",
        required=False,
        )

    real_name = TextLine(
        title=u"Full name",
        required=True,
        )

    role = TextLine(
        title=u"Role",
        required=True,
        )

    password = Password(
        title=u"Password",
        required=True,
        )

    def checkPassword(password):
        """Checks the given password against the stored one.
        """

        
@implementer(IUser, IContent)
class User(Base):

    __tablename__ = 'flg_user'
    
    login = Column(String(50), primary_key=True)
    email = Column(String(255))
    real_name = Column(String(150))
    role = Column(String(50))
    password = Column(String(16))

    def checkPassword(self, password):
        if password == self.password:
            return True
        return False

    @property
    def __content_type__(self):
        return self.__tablename__

    def getEmail(self):
        if self.email:
            return self.email
        return ""
