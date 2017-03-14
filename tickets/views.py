from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

from .tickets import app
from .models import Ticket, Organizer


@app.route('/api/v1/organizers')
def organizers():
    return jsonify({})


@app.route('/api/v1/organizers/<string:inn>/batches', methods=['POST'])
def create_batch(inn):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/batches/<int:batch_id>', methods=['GET'])
def get_batch(inn, batch_id):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/calculate_ticket_count', methods=['POST'])
def calculate_ticket_count(inn):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/ticket_count', methods=['GET'])
def get_ticket_count(inn):
    state = request.args['state']
    return jsonify({"count": Ticket.get_count_by_inn(inn, state)}), 201


@app.route('/api/v1/organizers/<string:inn>/tickets', methods=['GET'])
def get_tickets_by_organizer(inn):
    state = request.args['state']
    page = request.args.get('page', 1)
    limit = request.args.get('limit', 50)
    return jsonify([t.id for t in Ticket.by_inn(inn, state, page, limit)]), 201


@app.route('/api/v1/organizers/<string:inn>/tickets', methods=['POST'])
def create_ticket(inn):
    organizer = Organizer.by_inn(inn)
    if not Organizer.by_inn(inn):
        organizer = Organizer.create(inn)

    serial_number = request.json['serial_number']
    try:
        ticket = Ticket.create(organizer.id, serial_number)
    except IntegrityError:
        return jsonify({'collision': serial_number}), 409

    return jsonify({'id': ticket.id, 'serial_number': ticket.serial_number}), 201


@app.route('/api/v1/organizers/<string:inn>/tickets/<string:id_or_serial_number>', methods=['GET'])
def get_ticket(inn, id_or_serial_number):
    ticket = Ticket.by_inn_and_id_or_serial_number(inn, id_or_serial_number)
    if not ticket:
        return jsonify({}), 404

    return ticket.jsonify(), 201


@app.route('/api/v1/organizers/<string:inn>/tickets/<int:ticket_id>', methods=['PUT'])
def edit_ticket(inn, ticket_id):
    return "", 201


@app.route('/api/v1/organizers/<string:inn>/tickets/<int:ticket_id>/sell', methods=['POST'])
def sell_ticket(inn, ticket_id):
    Ticket.sell_by_inn_and_id(inn, ticket_id)
    return "", 201


@app.route('/api/v1/organizers/<string:inn>/tickets/<int:ticket_id>/cancel', methods=['POST'])
def cancel_ticket(inn, ticket_id):
    Ticket.cancel_by_inn_and_id(inn, ticket_id)
    return "", 201


@app.route('/api/v1/organizers/<string:inn>/csv_jobs', methods=['POST'])
def create_csv_job(inn):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/csv_jobs/<int:job_id>', methods=['GET'])
def get_csv_job(inn, job_id):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/stats', methods=['GET'])
def get_ticket_stats(inn):
    return jsonify({}), 201
