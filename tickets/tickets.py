from flask import Flask, request, jsonify

app = Flask(__name__)


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
    return jsonify({'count': None}), 201


@app.route('/api/v1/organizers/<string:inn>/tickets', methods=['POST'])
def create_ticket(inn):
    return jsonify({'id': None, 'serial_number': None}), 201


@app.route('/api/v1/organizers/<string:inn>/tickets/<string:id_or_serial_number>', methods=['GET'])
def get_ticket(inn, id_or_serial_number):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/tickets/<int:ticket_id>', methods=['PUT'])
def edit_ticket(inn, ticket_id):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/tickets/<int:ticket_id>/sell', methods=['POST'])
def sell_ticket(inn, ticket_id):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/tickets/<int:ticket_id>/cancel', methods=['POST'])
def cancel_ticket(inn, ticket_id):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/csv_jobs', methods=['POST'])
def create_csv_job(inn):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/csv_jobs/<int:job_id>', methods=['GET'])
def get_csv_job(inn, job_id):
    return jsonify({}), 201


@app.route('/api/v1/organizers/<string:inn>/stats', methods=['GET'])
def get_ticket_stats(inn):
    return jsonify({}), 201
