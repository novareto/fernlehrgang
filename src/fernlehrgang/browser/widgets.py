import grok

from zeam.form.ztk.widgets.textline import TextLineWidget
from zeam.form.ztk.widgets.choice import ChoiceFieldWidget
from zeam.form.ztk.widgets.bool import CheckBoxDisplayWidget
from zeam.form.ztk.widgets.number import NumberWidget
from zeam.form.ztk.widgets.choice import RadioFieldWidget


grok.templatedir("templates")


class UVCRadioFieldWidget(RadioFieldWidget):
    """Simple Override for removing <br> between choices"""


class HiddenDisplayWidget(TextLineWidget):
    grok.name("hiddendisplay")


class ChoiceHiddenDisplayWidget(ChoiceFieldWidget):
    grok.name("hiddendisplay")

    def getTermValue(self, value):
        return self.form.getContentData().get(self.component.identifier)

    def valueToUnicode(self, value):
        term = self.lookupTerm(value)
        if term is not None:
            return term.title
        return ""


class BoolHiddenDisplayWidget(CheckBoxDisplayWidget):
    grok.name("hiddendisplay")

    def checkValue(self, value):
        if value in ("No",):
            return False
        return True


class NumberWidget(NumberWidget):
    grok.name("hiddendisplay")
