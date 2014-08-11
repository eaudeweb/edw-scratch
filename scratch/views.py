from flask import render_template, request
from flask.views import View
from sqlalchemy import desc

from scratch.models import Tender, Winner, WorkerLog, db
from scratch.forms import TendersFilter, WinnerFilter, MAX, STEP


class GenericView(View):

    def render_template(self, context):
        return render_template(self.template_name, **context)

    def dispatch_request(self, *args, **kwargs):
        context = self.get_context(*args, **kwargs)
        return self.render_template(context)


class TendersFilterView(GenericView):
    def get_context(self):
        tenders = self.get_objects()

        if 'reset' in request.args:
            return {
                'tenders': tenders.all(),
                'filter_form': TendersFilter(),
                'reset': False,
            }

        organization = request.args.get('organization')
        status = request.args.get('status')
        favourite = request.args.get('favourite')

        if organization:
            tenders = tenders.filter_by(organization=organization)
        if status == 'closed':
            tenders = tenders.filter(Tender.winner != None)
        elif status == 'open':
            tenders = tenders.filter(Tender.winner == None)
        if favourite in ('True', 'False'):
            tenders = tenders.filter_by(favourite=eval(favourite))
        return {
            'tenders': tenders.all(),
            'filter_form': TendersFilter(
                organization=organization,
                status=status,
                favourite=favourite,
            ),
            'reset': organization or status or favourite,
        }


class TendersView(TendersFilterView):
    template_name = 'tenders.html'

    def get_objects(self):
        return (Tender.query
                .filter_by(hidden=False)
                .order_by(desc(Tender.published))
        )


class ArchiveView(TendersFilterView):
    template_name = 'archive.html'

    def get_objects(self):
        return (Tender.query
                .filter_by(hidden=True)
                .order_by(desc(Tender.published))
        )


class WinnersView(GenericView):
    template_name = 'winners.html'

    def get_context(self):
        winners = self.get_objects()
        if 'reset' in request.args:
            return {
                'winners': winners.all(),
                'filter_form': WinnerFilter(),
                'reset': False,
            }

        organization = request.args.get('organization')
        vendor = request.args.get('vendor')
        value = request.args.get('value')

        if organization:
            winners = winners.filter(
                Winner.tender.has(organization=organization)
            )
        if vendor:
            winners = winners.filter_by(vendor=vendor)
        if value:
            if value == 'max':
                winners = winners.filter(Winner.value >= MAX)
            else:
                winners = winners.filter(
                    Winner.value >= int(value),
                    Winner.value <= int(value) + STEP
                )

        return {
            'winners': winners.order_by(desc(Winner.award_date)).all(),
            'filter_form': WinnerFilter(
                organization=organization,
                vendor=vendor,
                value=value,
            ),
            'reset': organization or vendor or value
        }

    def get_objects(self):
        return Winner.query.filter(
            Winner.tender.has(hidden=False)
        ).order_by(desc(Winner.award_date))


class SearchView(GenericView):
    template_name = 'search.html'

    def get_context(self):
        query = request.args.get('query')
        context = {
            'query': query,
            'results': self.get_objects(query),
        }
        return context

    def get_objects(self, query):
        def _get_results(m):
            return m.query.whoosh_search(query).all()

        ids = set(
            [x.id for x in _get_results(Tender)] +
            [x.tender_id for x in _get_results(Winner)]
        )

        return Tender.query.filter(Tender.id.in_(ids)).all()


class TenderView(GenericView):
    template_name = 'tender.html'

    def get_context(self, **kwargs):
        tender_id = kwargs['tender_id']
        return {'tender': self.get_object(tender_id)}

    def get_object(self, tender_id):
        return Tender.query.get(tender_id)


class OverviewView(GenericView):
    template_name = 'overview.html'

    def get_context(self):
        from flask import current_app as app
        return {
            'last_updates': [d[0] for d in (
                WorkerLog.query
                .order_by(desc(WorkerLog.update))
                .with_entities(WorkerLog.update)
                .limit(15)
                .all()
            )],
            'emails': app.config['NOTIFY_EMAILS'],
        }


def toggle(tender_id, attribute):
    if not attribute in ('favourite', 'hidden'):
        return ''
    tender_object = Tender.query.get_or_404(tender_id)
    setattr(tender_object, attribute, not getattr(tender_object, attribute))
    db.session.commit()
    return '{0}'.format(getattr(tender_object, attribute))
