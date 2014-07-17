from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey
)
from flask.ext.script import Manager
from sqlalchemy.orm import relationship
from flask.ext.sqlalchemy import SQLAlchemy

db_manager = Manager()
db = SQLAlchemy()


class Tender(db.Model):
    __tablename__ = 'tender'

    id = Column(Integer, primary_key=True)
    reference = Column(String(255), unique=True)
    title = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    published = Column(Date)
    deadline = Column(DateTime, nullable=True)

    def __unicode__(self):
        return 'Tender notice: %s' % self.title


class TenderDocument(db.Model):
    __tablename__ = 'tender_document'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)

    tender_id = Column(ForeignKey('tender.id'), nullable=True)
    tender = relationship("Tender", backref="documents")


class Winner(db.Model):
    __tablename__ = 'winner'

    id = Column(Integer, primary_key=True)
    vendor = Column(String(255), nullable=True)
    value = Column(Float, nullable=True)
    award_date = Column(DateTime)

    tender_id = Column(ForeignKey('tender.id'), nullable=True)
    tender = relationship("Tender", backref="winner")

    def __unicode__(self):
        return '%s WON BY %s' % (self.title, self.vendor)


@db_manager.command
def init():
    db.create_all()
