from wtforms import Form, SelectField
from scratch.models import Tender, Winner


class TendersFilter(Form):

    organization = SelectField(u'Organization')
    title = SelectField(u'Title')

    def __init__(self, **kwargs):
        super(TendersFilter, self).__init__(**kwargs)

        self.organization.choices = [('', 'All Organizations')] + [
            (o.organization, o.organization)
            for o in Tender.query
            .with_entities(Tender.organization)
            .distinct()
        ]

        self.title.choices = [('', 'All Titles')] + [
            (o.title, o.title)
            for o in Tender.query
            .with_entities(Tender.title)
            .distinct()
        ]


class WinnerFilter(Form):

    organization = SelectField(u'Organization')
    vendor = SelectField(u'Vendor')

    def __init__(self, **kwargs):
        super(WinnerFilter, self).__init__(**kwargs)

        self.organization.choices = ([('', 'All Organizations')] + [
            (w.tender.organization, w.tender.organization)
            for w in Winner.query.join(Winner.tender)
        ])

        self.vendor.choices = [('', 'All Vendors')] + [
            (o.vendor, o.vendor)
            for o in Winner.query
            .with_entities(Winner.vendor)
            .distinct()
        ]
