import datetime

from scratch.models import (
    Tender, Winner, save_tender, save_winner, update_tender,
    save_document_to_filesystem, save_document_to_models,
)
from scratch.ungm_scraper import (
    parse_tenders_list, parse_winners_list, parse_tender, parse_winner,
)
from scratch.utils import string_to_date


def get_new_winners(request_cls):
    saved_winners = (
        Winner.query
        .with_entities(Winner.tender)
        .with_entities(Tender.reference)
        .all()
    )

    requested_html_winners = request_cls.request_winners_list()
    if not requested_html_winners:
        return []
    requested_winners = parse_winners_list(requested_html_winners)

    new_winners = filter(
        lambda x: (x['reference'], ) not in saved_winners,
        requested_winners
    )

    if not new_winners:
        return []

    for new_winner in new_winners:
        html_data = request_cls.get_request(new_winner['url'])
        tender_fields, winner_fields = parse_winner(html_data)
        tender = save_winner(tender_fields, winner_fields)
        update_tender(tender, 'url', new_winner['url'])


def get_new_tenders(last_date, request_cls):
    last_references = (
        Tender.query
        .filter(Tender.published >= last_date)
        .with_entities(Tender.reference)
        .all()
    )

    requested_html_tenders = request_cls.request_tenders_list()
    if not requested_html_tenders:
        return []
    extracted_tenders = parse_tenders_list(requested_html_tenders)
    new_tenders = filter(
        lambda x: (
            string_to_date(x['published']) >= last_date and
            (x['reference'], ) not in last_references
        ),
        extracted_tenders
    )

    if not new_tenders:
        return []

    for new_tender in new_tenders:
        url = new_tender['url']
        html_data = request_cls.get_request(url)
        tender_fields = parse_tender(html_data)
        tender_fields.update({'url': url})
        tender = save_tender(tender_fields)
        for document in tender_fields['documents']:
            save_document_to_filesystem(document, str(tender.id), request_cls)


def get_favorite_tenders():
    tenders = (Tender.query
               .filter_by(favourite=True, source='UNGM')
               .filter(Tender.deadline is not None and
                       Tender.deadline > datetime.datetime.now()))
    return tenders.all()


def scrap_favorites(request_cls):
    favorites = get_favorite_tenders()
    changed_tenders = []
    for tender in favorites:
        html_data = request_cls.get_request(tender.url)
        tender_fields = parse_tender(html_data)

        attr_changes = {}
        for attr, value in [(k, v) for (k, v) in tender_fields.items()
                            if k != 'documents']:
            old_value = getattr(tender, attr)
            if value != old_value:
                attr_changes.update({attr: (old_value, value)})
                update_tender(tender, attr, value)

        received_docs = tender_fields['documents']
        saved_docs = [
            {'name': d.name, 'download_url': d.download_url}
            for d in tender.documents
        ]

        new_docs = []
        for document in received_docs:
            if document not in saved_docs:
                new_docs.append(document)
                save_document_to_models(tender, document)
                save_document_to_filesystem(document, str(tender.id),
                                            request_cls)

        if attr_changes or new_docs:
            changed_tenders.append((tender, attr_changes, new_docs))

    return changed_tenders
