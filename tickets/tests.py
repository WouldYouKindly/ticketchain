import os
import json
import unittest
import tempfile

from tickets.views import *
from tickets.app import app


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            app.db.create_all()

    def tearDown(self):
        with app.app_context():
            app.db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_create_ticket_success(self):
        inn = 'abcd1234'
        serial_number = 'AB123456'
        response = self.app.post(f'/api/v1/organizers/<string:inn>/tickets',
                                 data=json.dumps({'serial_number': serial_number}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 201)

        response_json = json.loads(response.data)
        self.assertTrue('serial_number' in response_json, 'Response should contain '
                                                          'serial number sent in request.')
        self.assertTrue('id' in response_json, 'Response should contatin id '
                                               'assigned to a ticket.')
        self.assertEqual(response_json['serial_number'], serial_number,
                         'Serial numbers in request and response differ.')
        self.assertIsInstance(response_json['id'], int, 'Id of a ticket is not an integer')

    def test_create_ticket_collision(self):
        inn = 'abcd1234'
        serial_number = 'AB123456'
        first_response = self.app.post(f'/api/v1/organizers/<string:inn>/tickets',
                                       data=json.dumps({'serial_number': serial_number}),
                                       content_type='application/json')
        response = self.app.post(f'/api/v1/organizers/<string:inn>/tickets',
                                 data=json.dumps({'serial_number': serial_number}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 409)
        response_json = json.loads(response.data)
        self.assertEqual(response_json['collision'], serial_number, 'Response should contain'
                                                                    '"collision" field.')

    def test_get_ticket_by_id_success(self):
        # Let's create a ticket
        inn = 'abcd1234'
        serial_number = 'AB123456'
        response = self.app.post(f'/api/v1/organizers/{inn}/tickets',
                                 data=json.dumps({'serial_number': serial_number}),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        ticket_id = response_json['id']

        # And test that it's created
        ticket = self.app.get(f'/api/v1/organizers/{inn}/tickets/{ticket_id}')

        self.assertEqual(ticket.status_code, 201)

        ticket_json = json.loads(ticket.data)

        for i in ('serial_number', 'state', 'created_date', 'contract_address', 'id'):
            self.assertTrue(i in ticket_json, f"Reponse should contain field '{i}'")

    def test_get_ticket_by_serial_number_success(self):
        # Let's create a ticket
        inn = 'abcd1234'
        serial_number = 'AB123456'
        response = self.app.post(f'/api/v1/organizers/{inn}/tickets',
                                 data=json.dumps({'serial_number': serial_number}),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        ticket_id = response_json['id']

        # And test that it's created
        ticket = self.app.get(f'/api/v1/organizers/{inn}/tickets/{serial_number}')

        self.assertEqual(ticket.status_code, 201)

        ticket_json = json.loads(ticket.data)

        for i in ('serial_number', 'state', 'created_date', 'contract_address', 'id'):
            self.assertTrue(i in ticket_json, f"Reponse should contain field '{i}'")

    def test_get_ticket_by_nonexistent_inn_and_id_failure(self):
        inn = 'abcd1234'
        ticket_id = 1984

        response = self.app.get(f'/api/v1/organizers/{inn}/tickets/{ticket_id}')
        self.assertEqual(response.status_code, 404)

    def test_get_ticket_by_nonexistent_id_failure(self):
        inn = 'abcd1234'
        serial_number = 'AB123456'
        self.app.post(f'/api/v1/organizers/{inn}/tickets',
                      data=json.dumps({'serial_number': serial_number}),
                      content_type='application/json')

        # We know that id is an autoincrementing integer starting at 1. 1984 wouldn't exist
        ticket_id = 1984

        response = self.app.get(f'/api/v1/organizers/{inn}/tickets/{ticket_id}')
        self.assertEqual(response.status_code, 404)

    def test_sell_ticket(self):
        # Let's create a ticket
        inn = 'abcd1234'
        serial_number = 'AB123456'
        response = self.app.post(f'/api/v1/organizers/{inn}/tickets',
                                 data=json.dumps({'serial_number': serial_number}),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        ticket_id = response_json['id']

        # Sell it
        response = self.app.post(f'/api/v1/organizers/{inn}/tickets/{ticket_id}/sell')
        self.assertEqual(response.status_code, 201)

        # And see that it's state is now 'sold'
        ticket = self.app.get(f'/api/v1/organizers/{inn}/tickets/{serial_number}')
        ticket_json = json.loads(ticket.data)

        self.assertEqual(ticket_json['state'], 'sold', "Ticket's state should be 'sold' "
                                                       "after it's been sold.")

    def test_cancel_ticket(self):
        # Let's create a ticket
        inn = 'abcd1234'
        serial_number = 'AB123456'
        response = self.app.post(f'/api/v1/organizers/{inn}/tickets',
                                 data=json.dumps({'serial_number': serial_number}),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        ticket_id = response_json['id']

        # Sell it
        response = self.app.post(f'/api/v1/organizers/{inn}/tickets/{ticket_id}/cancel')
        self.assertEqual(response.status_code, 201)

        # And see that it's state is now 'sold'
        ticket = self.app.get(f'/api/v1/organizers/{inn}/tickets/{serial_number}')
        ticket_json = json.loads(ticket.data)

        self.assertEqual(ticket_json['state'], 'cancelled',
                         "Ticket's state should be 'cancelled' after it's been cancelled.")

    def test_get_ticket_count(self):
        inn = 'abcd1234'

        num_tickets = 100
        for i in range(num_tickets):
            serial_number = 'AB' + str(123456 + i)
            self.app.post(f'/api/v1/organizers/{inn}/tickets',
                          data=json.dumps({'serial_number': serial_number}),
                          content_type='application/json')

        # There should be 100 created tickets
        response = self.app.get(f'/api/v1/organizers/{inn}/ticket_count?state=created')

        self.assertEqual(response.status_code, 201)

        response_json = json.loads(response.data)
        self.assertEqual(response_json['count'], num_tickets)

        # but zero sold
        response = self.app.get(f'/api/v1/organizers/{inn}/ticket_count?state=sold')

        self.assertEqual(response.status_code, 201)

        response_json = json.loads(response.data)
        self.assertEqual(response_json['count'], 0)

        # and zero cancelled
        response = self.app.get(f'/api/v1/organizers/{inn}/ticket_count?state=cancelled')

        self.assertEqual(response.status_code, 201)

        response_json = json.loads(response.data)
        self.assertEqual(response_json['count'], 0)

    def test_get_tickets_by_organizer(self):
        inn = 'abcd1234'

        num_tickets = 100
        for i in range(num_tickets):
            serial_number = 'AB' + str(123456 + i)
            self.app.post(f'/api/v1/organizers/{inn}/tickets',
                          data=json.dumps({'serial_number': serial_number}),
                          content_type='application/json')

        # Let's ask for default paging params
        response = self.app.get(f'/api/v1/organizers/{inn}/tickets?state=created')
        self.assertEqual(response.status_code, 201)

        response_json = json.loads(response.data)
        self.assertIsInstance(response_json, list, 'Should returns an array of ticket IDs')
        self.assertEqual(len(response_json), 50, 'Default page size should be 50')
        self.assertTrue(all(isinstance(i, int) for i in response_json),
                        'All ticket IDs should be integers')

        # And non-default too
        response = self.app.get(
            f'/api/v1/organizers/{inn}/tickets?state=created&page=3&limit=15')

        self.assertEqual(response.status_code, 201)

        response_json = json.loads(response.data)

        self.assertEqual(len(response_json), 15)

    def test_edit_ticket(self):
        # Let's create a ticket
        inn = 'abcd1234'
        serial_number = 'AB123456'
        response = self.app.post(f'/api/v1/organizers/{inn}/tickets',
                                 data=json.dumps({'serial_number': serial_number}),
                                 content_type='application/json')
        response_json = json.loads(response.data)
        ticket_id = response_json['id']

        info = {
            "price_rub": 120,
            "is_paper_ticket": False,
            "issuer": "TicketChain",
            "issuer_inn": "111111111145",
            "issuer_ogrn": "7811111111123",
            "issuer_ogrnip": "221111111112345",
            "issuer_address": "",
            "event_title": "",
            "event_place_title": "",
            "event_date": "15.03.2017 18:00",
            "event_place_address": "",
            "row": "17",
            "seat": "9",
            "ticket_category": "1",
            "seller": "TicketLand company",
            "seller_inn": "1234567812",
            "seller_ogrn": "1234567812123",
            "seller_ogrnip": "123456781212345",
            "seller_address": "",
            "buyer_name": "Alexey Key",
            "buying_date": "12.03.2017 12:16"
        }
        response = self.app.put(f'/api/v1/organizers/{inn}/tickets/{ticket_id}',
                                 data=json.dumps(info),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)

        ticket = self.app.get(f'/api/v1/organizers/{inn}/tickets/{serial_number}')
        ticket_json = json.loads(ticket.data)

        for key in info.keys():
            self.assertTrue(key in ticket_json)
            self.assertTrue(ticket_json[key] == info[key])

if __name__ == '__main__':
    unittest.main()