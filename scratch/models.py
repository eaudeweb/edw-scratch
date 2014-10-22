import argparse
import os
from datetime import date

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Boolean,
    Enum, desc,
)
from flask.ext.script import Manager
from sqlalchemy.orm import relationship
from flask.ext.sqlalchemy import SQLAlchemy
from flask import current_app

from scratch.utils import has_save_permission

db_manager = Manager()
db = SQLAlchemy()


class Tender(db.Model):
    __tablename__ = 'tender'
    __searchable__ = ['title', 'reference', 'organization', 'description']

    id = Column(Integer, primary_key=True)
    reference = Column(String(255), unique=True)
    notice_type = Column(String(255))
    title = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    published = Column(Date)
    deadline = Column(DateTime, nullable=True)
    description = Column(Text(5095), nullable=True)
    favourite = Column(Boolean, default=False)
    notified = Column(Boolean, default=False)
    url = Column(String(255))
    hidden = Column(Boolean, default=False)
    source = Column(Enum('UNGM', 'TED'))
    unspsc_codes = Column(String(1024))

    documents = relationship("TenderDocument", backref="tender")
    winner = relationship("Winner", backref="tender")

    def __unicode__(self):
        return 'Tender notice: %s' % self.title


class TenderDocument(db.Model):
    __tablename__ = 'tender_document'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    download_url = Column(String(255))

    tender_id = Column(ForeignKey('tender.id'), nullable=True)


class Winner(db.Model):
    __tablename__ = 'winner'
    __searchable__ = ['vendor']

    id = Column(Integer, primary_key=True)
    vendor = Column(String(255), nullable=True)
    value = Column(Float, nullable=True)
    currency = Column(String(3), nullable=True)
    award_date = Column(Date)
    notified = Column(Boolean, default=False)

    tender_id = Column(ForeignKey('tender.id'), nullable=True)

    def __unicode__(self):
        return '%s WON BY %s' % (self.title, self.vendor)


class WorkerLog(db.Model):
    __tablename__ = 'worker_log'

    id = Column(Integer, primary_key=True)
    update = Column(Date)
    source = Column(Enum('UNGM', 'TED'))


def last_update(source):
    worker_log = (
        WorkerLog.query
        .filter_by(source=source)
        .order_by(desc(WorkerLog.update))
        .first()
    )
    return worker_log.update if worker_log else None


def save_tender(tender):
    old_tender = Tender.query.filter_by(reference=tender['reference']).first()
    if old_tender:
        for attr, value in [(k, v) for (k, v) in tender.items()
                            if k != 'documents']:
            update_tender(old_tender, attr, value)
        return old_tender

    documents = tender.pop('documents', [])
    tender_entry = Tender(**tender)
    db.session.add(tender_entry)
    db.session.commit()
    for document in documents:
        save_document_to_models(tender_entry, document)
    tender['documents'] = documents

    return tender_entry


def save_document_to_models(tender, document):
    document_entry = TenderDocument(tender=tender, **document)
    db.session.add(document_entry)
    db.session.commit()


@has_save_permission
def save_document_to_filesystem(document, dirname, request_cls):
    doc = request_cls.request_document(document['download_url'])
    if doc:
        filename = document['name']
        path = os.path.join(current_app.config.get('FILES_DIR'), dirname)
        save_file(path, filename, doc)


def save_file(path, filename, content):
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


def save_winner(tender_fields, winner_fields):
    tender = Tender.query.filter_by(**tender_fields).first()
    if not tender:
        tender_entry = Tender(**tender_fields)
        db.session.add(tender_entry)
        db.session.commit()
        set_notified(tender_entry)
    else:
        tender_entry = tender
    winner_entry = Winner(tender=tender_entry, **winner_fields)
    db.session.add(winner_entry)
    db.session.commit()

    return tender_entry


def set_notified(tender_or_winner):
    tender_or_winner.notified = True
    db.session.commit()


def add_worker_log(source, new_date=None):
    log = WorkerLog(source=source, update=new_date or date.today())
    db.session.add(log)
    db.session.commit()


def update_tender(tender, attribute, value):
    setattr(tender, attribute, value)
    db.session.commit()


@db_manager.option('alembic_args', nargs=argparse.REMAINDER)
def alembic(alembic_args):
    from alembic.config import CommandLine

    CommandLine().main(argv=alembic_args)


@db_manager.command
def revision(message=None):
    if message is None:
        message = raw_input('revision name: ')
    return alembic(['revision', '--autogenerate', '-m', message])


@db_manager.command
def upgrade(revision='head'):
    return alembic(['upgrade', revision])


@db_manager.command
def downgrade(revision):
    return alembic(['downgrade', revision])
