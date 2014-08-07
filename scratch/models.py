from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Boolean,
    desc,
)
from flask.ext.script import Manager
from sqlalchemy.orm import relationship
from flask.ext.sqlalchemy import SQLAlchemy

from scratch.custom_filters import datetime_filter


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
    award_date = Column(Date)
    notified = Column(Boolean, default=False)

    tender_id = Column(ForeignKey('tender.id'), nullable=True)

    def __unicode__(self):
        return '%s WON BY %s' % (self.title, self.vendor)


class WorkerLog(db.Model):
    __tablename__ = 'worker_log'

    id = Column(Integer, primary_key=True)
    update = Column(Date)

    def __unicode__(self):
        return 'Last update on ' % datetime_filter(self.update)


def last_update():
    WorkerLog.query.order_by(desc(WorkerLog.update)).first()


def save_tender(tender):
    documents = tender.pop('documents')
    tender_entry = Tender(**tender)
    db.session.add(tender_entry)
    db.session.commit()
    for document in documents:
        document_entry = TenderDocument(tender=tender_entry, **document)
        db.session.add(document_entry)
    db.session.commit()
    tender['documents'] = documents

    return tender_entry.id


def save_winner(tender_fields, winner_fields):
    tender = Tender.query.filter_by(**tender_fields).first()
    if not tender:
        tender_entry = Tender(**tender_fields)
        db.session.add(tender_entry)
        db.session.commit()
    else:
        tender_entry = tender
    winner_entry = Winner(tender=tender_entry, **winner_fields)
    db.session.add(winner_entry)
    db.session.commit()

    return tender_entry.id
