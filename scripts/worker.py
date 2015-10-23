# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


from zope import component
from z3c.saconfig import Session
from fernlehrgang.tasks import notifications_for_ofg


def worker():
    flg = root['flg']
    component.hooks.setSite(flg)
    session = Session()
    notifications_for_ofg()


if __name__ == "__main__":
    worker()
    exit()
