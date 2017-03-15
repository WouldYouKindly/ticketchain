import json
from random import randint
from datetime import datetime

from .app import db


class Organizer(db.Model):
    __tablename__ = 'organizers'
    id = db.Column(db.Integer, primary_key=True)
    inn = db.Column(db.String, nullable=False)

    @staticmethod
    def by_inn(inn):
        return db.session.query(Organizer).filter_by(inn=inn).first()

    @staticmethod
    def create(inn):
        org = Organizer(inn=inn)
        db.session.add(org)
        db.session.commit()
        return org


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('organizers.id'), nullable=False)
    serial_number = db.Column(db.String, nullable=False, unique=True)
    state = db.Column(db.String, nullable=False,
                      doc='Either "created", "cancelled" or "sold"')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    contract_address = db.Column(db.Integer, unique=True)
    info = db.Column(db.String)  # cause we use SQLite and it doesn't have JSON type

    def jsonify(self):
        ticket = {
            "serial_number": self.serial_number,
            "id": self.id,
            "state": self.state,
            "created_date": self.created_at.strftime('%d.%m.%Y %H:%M'),
            "contract_address": self.contract_address
        }

        info = self.info or "{}"
        ticket.update(json.loads(info))

        return json.dumps(ticket)

    def sell(self):
        self.state = 'sold'
        db.session.commit()

    def cancel(self):
        self.state = 'cancelled'
        db.session.commit()

    def set_info(self, info):
        self.info = json.dumps(info)
        db.session.commit()

    @staticmethod
    def by_inn(inn, state, page=1, limit=50):
        return db.session.query(Ticket).\
            join(Organizer, Organizer.id == Ticket.organizer_id).\
            filter(Organizer.inn == inn,
                   Ticket.state == state).\
            offset((page - 1) * limit). \
            limit(limit). \
            all()

    @staticmethod
    def get_count_by_inn(inn, state):
        return db.session.query(Ticket). \
            join(Organizer, Organizer.id == Ticket.organizer_id). \
            filter(Organizer.inn == inn,
                   Ticket.state == state). \
            count()

    @staticmethod
    def by_inn_and_id_or_serial_number(inn, id_or_serial_number):
        return db.session.query(Ticket).\
            join(Organizer, Organizer.id == Ticket.organizer_id). \
            filter(Organizer.inn == inn,
                   db.or_(Ticket.id == id_or_serial_number,
                          Ticket.serial_number == id_or_serial_number)).\
            first()

    @staticmethod
    def create(organizer_id, serial_number):
        # TODO make sure contract address is unique
        t = Ticket(organizer_id=organizer_id,
                   serial_number=serial_number,
                   state='created',
                   contract_address=randint(1, 1000000000000))
        db.session.add(t)
        db.session.commit()
        return t

