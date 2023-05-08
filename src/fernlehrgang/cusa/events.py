import grok

from zope.interface.interfaces import IObjectEvent
from fernlehrgang import log
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.interfaces.teilnehmer import ITeilnehmer
from fernlehrgang.interfaces.antwort import IAntwort
from fernlehrgang.interfaces.cusa_result import ICusaResult


@grok.subscribe(grok.IObjectModifiedEvent)
def handle_cusa_result_on_edit(obj):
    unternehmen = None
    context = obj.object
    log("Update CUSA Result on EDIT %s " % context)
    if IKursteilnehmer.providedBy(context):
        unternehmen = context.unternehmen
    elif ITeilnehmer.providedBy(context):
        for unt in context.unternehmen:
            if unt.mnr == context.unternehmen_mnr:
                unternehmen = unt
    elif IAntwort.providedBy(context):
        unternehmen = context.kursteilnehmer.unternehmen
    else:
        log('No Handler CUSAResult for context %s on Edit' % context)
    if unternehmen:
        ICusaResult(unternehmen).persist()


@grok.subscribe(grok.IObjectAddedEvent)
def handle_cusa_result_on_add(obj):
    unternehmen = None
    context = obj.object
    log("Update CUSA Result on ADD %s " % context)
    if IKursteilnehmer.providedBy(context):
        unternehmen = context.unternehmen
    elif ITeilnehmer.providedBy(context):
        for unt in context.unternehmen:
            if unt.mnr == context.unternehmen_mnr:
                unternehmen = unt
    elif IAntwort.providedBy(context):
        unternehmen = context.kursteilnehmer.unternehmen
    else:
        log('No Handler CUSAResult for context %s on Add' % context)

    if unternehmen:
        ICusaResult(unternehmen).persist()
