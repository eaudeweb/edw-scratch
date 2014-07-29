from wtforms import Form, SelectField
from scratch.models import Tender, Winner


MAX = 220000
STEP = 20000


class TendersFilter(Form):

    organization = SelectField(u'Organization')
    title = SelectField(u'Title')
    status = SelectField(u'Status', choices=[
        ('', 'All Values'),
        ('open', 'OPEN'),
        ('closed', 'CLOSED'),
    ])

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
    r = range(0, MAX, STEP)
    VALUE_CHOICES = [('', 'All Values')] + (
        zip(
            map(lambda x: str(x), r),
            ['%s - %s' % (format(x, ',d'), format(y, ',d'))
             for (x, y) in zip(r[:-1], r[1:])]
        ) + [('max', '>%s' % format(MAX-STEP, ',d'))]
    )

    organization = SelectField(u'Organization')
    vendor = SelectField(u'Vendor')
    value = SelectField(u'Value', coerce=str, choices=VALUE_CHOICES)

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
