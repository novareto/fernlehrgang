# -*- coding: utf-8 -*-

import grok
from grokcore.component import Subscription, queryOrderedSubscriptions
from fernlehrgang.models import Teilnehmer, Fernlehrgang, Lehrheft
from zope.securitypolicy.zopepolicy import ZopeSecurityPolicy
from zope.interface import Interface
from zope.browser.interfaces import IBrowserView
from zope.security.proxy import removeSecurityProxy


class ISecurityBypass(Interface):
    
    def __call__(request, permission):
        """Returns a Boolean or None.
        True: allowed. The rest of the security check is ignored.
        False: unauthorized. The rest of the security check is ignored.
        None: No definitive decision. The security continues as normal.
        """


def bypass(policy, permission, context):
    context = removeSecurityProxy(context)
    bypassers = queryOrderedSubscriptions(context, ISecurityBypass)
    for bypass in bypassers:
        result = bypass(policy, permission, context)
        if result is not None:
            return result
    return None
        
        
class SecurityPolicy(ZopeSecurityPolicy):

    def checkPermission(self, permission, object):
        bypassed = bypass(self, permission, object)
        if bypassed is not None:
            return bypassed
        return ZopeSecurityPolicy.checkPermission(self, permission, object)


class ViewDelegation(Subscription):
    """Generic subscriber for the views:
    If a view is published, we try and see if its context
    doesn't have a bypasser instead.
    """
    grok.context(IBrowserView)
    grok.implements(ISecurityBypass)
    grok.order(100)

    def __call__(self, policy, permission, context):
        return bypass(policy, permission, context.context)

    
class LehrheftWatchDog(Subscription):
    grok.context(Lehrheft)
    grok.implements(ISecurityBypass)
    grok.order(1)

    def __call__(self, policy, context, permission):
        assert policy.participations
        request = policy.participations[0]
        print "Handle Lehrheft security here"
