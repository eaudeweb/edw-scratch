from wtforms import Form, SelectField
from scratch.models import Tender


class OrganizationFilter(Form):

    organization = SelectField(u'Organization')

    def __init__(self, **kwargs):
        super(OrganizationFilter, self).__init__(**kwargs)

        self.organization.choices = [('', 'All Organizations')] + [
            (o.organization, o.organization)
            for o in Tender.query
            .with_entities(Tender.organization)
            .distinct()
        ]
