import grok

from dataclasses import dataclass
from zope.interface import implementer
from fernlehrgang.interfaces.cusa_result import ICusaResult
from fernlehrgang.interfaces.unternehmen import IUnternehmen
from fernlehrgang.interfaces.kursteilnehmer import IKursteilnehmer
from fernlehrgang.browser.ergebnisse import ICalculateResults
from fernlehrgang import models
from z3c.saconfig import Session
from io import StringIO
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


@dataclass
class CUSAResult:
    status: str = ""
    message: str = ""
    flg: str = ""
    kompetenzzentrum: str = ""
    titel: str = ""
    name: str = ""


@implementer(ICusaResult)
class CusaResult(grok.Adapter):
    grok.context(IUnternehmen)

    def get_kursteilnehmer(self):
        ktns = []
        for teilnehmer in self.context.teilnehmer:
            for ktn in teilnehmer.kursteilnehmer:
                ktns.append(ktn)
        return sorted(ktns, key=lambda x: x.fernlehrgang_id, reverse=True)

    def calculate(self):
        if len(self.context.teilnehmer) == 0:
            result = CUSAResult(
                status="nicht angelegt", message="kein Unternehmermodell BGHW"
            )
            return result

        def isActive(ktn):
            if ktn.status == "A1":
                return ktn
            return

        def wrongStatus(ktn):
            return IKursteilnehmer["status"].source(None).getTerm(ktn.status).title

        result = []
        if len(self.get_kursteilnehmer()) == 0:
            result = CUSAResult(
                status="nicht angelegt", message="Kein Unternehmermodel BGHW"
            )
            return result

        for ktn in self.get_kursteilnehmer():
            if isActive(ktn):
                flg_result = ICalculateResults(ktn).summary()
                if "Nicht Bestanden" in flg_result.get("comment"):
                    result.append(
                        CUSAResult(
                            status=wrongStatus(ktn),
                            message=flg_result.get("comment"),
                            kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                            flg=ktn.fernlehrgang.jahr,
                            titel=ktn.fernlehrgang.titel,
                            name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                        )
                    )
                else:
                    return CUSAResult(
                        status=wrongStatus(ktn),
                        message=flg_result.get("comment"),
                        kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                        flg=ktn.fernlehrgang.jahr,
                        titel=ktn.fernlehrgang.titel,
                        name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                    )
            elif wrongStatus(ktn):
                if ktn.status == "A2":
                    result.append(
                        CUSAResult(
                            status=wrongStatus(ktn),
                            message="nicht bestanden (kein TN angemeldet)",
                            kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                            flg=ktn.fernlehrgang.jahr,
                            titel=ktn.fernlehrgang.titel,
                            name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                        )
                    )
                elif ktn.status == "L9":
                    result.append(
                        CUSAResult(
                            status=wrongStatus(ktn),
                            message="nicht bestanden (keine Berechtigung)",
                            kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                            flg=ktn.fernlehrgang.jahr,
                            titel=ktn.fernlehrgang.titel,
                            name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                        )
                    )
                elif ktn.status == "L8":
                    result.append(
                        CUSAResult(
                            status=wrongStatus(ktn),
                            message="nicht bestanden (keine Berechtigung)",
                            kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                            flg=ktn.fernlehrgang.jahr,
                            titel=ktn.fernlehrgang.titel,
                            name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                        )
                    )
                elif ktn.status == "L7":
                    result.append(
                        CUSAResult(
                            status=wrongStatus(ktn),
                            message="nicht bestanden (TN ausgeschieden)",
                            kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                            flg=ktn.fernlehrgang.jahr,
                            titel=ktn.fernlehrgang.titel,
                            name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                        )
                    )
                elif ktn.status == "L4":
                    result.append(
                        CUSAResult(
                            status=wrongStatus(ktn),
                            message="nicht bestanden",
                            kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                            flg=ktn.fernlehrgang.jahr,
                            titel=ktn.fernlehrgang.titel,
                            name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                        )
                    )
                elif ktn.status == "S1":
                    result.append(
                        CUSAResult(
                            status=wrongStatus(ktn),
                            message="nicht bestanden (Export Notiz)",
                            kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                            flg=ktn.fernlehrgang.jahr,
                            titel=ktn.fernlehrgang.titel,
                            name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                        )
                    )
                elif ktn.status == "Z1":
                    result.append(
                        CUSAResult(
                            status=wrongStatus(ktn),
                            message="nicht bestanden",
                            kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                            flg=ktn.fernlehrgang.jahr,
                            titel=ktn.fernlehrgang.titel,
                            name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                        )
                    )
                else:
                    result.append(
                        CUSAResult(
                            status=wrongStatus(ktn),
                            message="Teilnahme nicht erforderlich",
                            kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                            flg=ktn.fernlehrgang.jahr,
                            titel=ktn.fernlehrgang.titel,
                            name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                        )
                    )
            else:
                result.append(
                    CUSAResult(
                        message="NOT ACTIVE",
                        status="interner Fehler",
                        kompetenzzentrum=ktn.teilnehmer.kompetenzzentrum,
                        flg=ktn.fernlehrgang.jahr,
                        titel=ktn.fernlehrgang.titel,
                        name="%s, %s" % (ktn.teilnehmer.name, ktn.teilnehmer.vorname)
                    )
                )
        return result.pop()



    def persist(self):
        result = self.calculate()
        session = Session()
        def kzentrum(kzentrum):
            if kzentrum:
                return kzentrum.capitalize()
            return kzentrum
        cr = models.CUSAResult(
            ergebnis=''.join(strip_tags(result.message).strip()),
            status=strip_tags(result.status),
            unternehmen_mnr=self.context.mnr,
            fernlehrgang_jahr=result.flg,
            lehrgang=result.titel,
            name=result.name,
            kompetenzzentrum=kzentrum(result.kompetenzzentrum),
        )
        #import pdb; pdb.set_trace()
        session.merge(cr)
        return result
