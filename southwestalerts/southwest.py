import json
import requests


API_KEY = 'l7xx12ebcbc825eb480faa276e7f192d98d1'  # TODO: Retrieve this from https://mobile.southwest.com/js/config.js
BASE_URL = 'https://mobile.southwest.com'


class Southwest(object):
    def __init__(self, username, password):
        self._session = _SouthwestSession(username, password)

    def get_upcoming_trips(self):
        return self._session.get('/api/customer/v1/accounts/account-number/{}/upcoming-trips'.format(self._session.account_number))

    def start_change_flight(self, record_locator, first_name, last_name):
        """Start the flight change process.

        This returns the flight including itinerary."""
        resp = self._session.get('/api/extensions/v1/mobile/reservations/record-locator/{record_locator}?first-name={first_name}&last-name={last_name}&action=CHANGE'.format(
            record_locator=record_locator,
            first_name=first_name,
            last_name=last_name
        ))
        return resp

    def get_available_change_flights(self, record_locator, first_name, last_name, departure_date, origin_airport, destination_airport):
        """Select a specific flight and continue the checkout process."""
        url = '/api/extensions/v1/mobile/reservations/record-locator/{record_locator}/products?first-name={first_name}&last-name={last_name}&is-senior-passenger=false&trip%5B%5D%5Borigination%5D={origin_airport}&trip%5B%5D%5Bdestination%5D={destination_airport}&trip%5B%5D%5Bdeparture-date%5D={departure_date}'.format(
            record_locator=record_locator,
            first_name=first_name,
            last_name=last_name,
            origin_airport=origin_airport,
            destination_airport=destination_airport,
            departure_date=departure_date
        )
        return self._session.get(url)

    def get_price_change_flight(self, record_locator, first_name, last_name, product_id):
        url = '/api/reservations-api/v1/air-reservations/reservations/record-locator/{record_locator}/prices?first-name={first_name}&last-name={last_name}&product-id%5B%5D={product_id}'.format(
            record_locator=record_locator,
            first_name=first_name,
            last_name=last_name,
            product_id=product_id
        )
        return self._session.get(url)


class _SouthwestSession():
    def __init__(self, username, password):
        self._session = requests.Session()
        self._login(username, password)

    def _login(self, username, password):
        data = self.post('/api/customer/v1/accounts/login', payload={
            'accountNumberOrUserName': username,
            'password': password
        })
        self.account_number = data['accessTokenDetails']['accountNumber']
        self.access_token = data['accessToken']

    def get(self, path, success_codes=[200]):
        resp = self._session.get(self._get_url(path), headers=self._get_headers())
        return self._parsed_response(resp, success_codes=success_codes)

    def post(self, path, payload, success_codes=[200]):
        resp = self._session.post(self._get_url(path), data=json.dumps(payload), headers=self._get_headers())
        return self._parsed_response(resp, success_codes=success_codes)

    @staticmethod
    def _get_url(path):
        return '{}{}'.format(BASE_URL, path)

    def _get_headers(self):
        return {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/vnd.swacorp.com.accounts.login-v1.0+json',
            'token': self.access_token if hasattr(self, 'access_token') else None
        }

    @staticmethod
    def _parsed_response(response, success_codes=[200]):
        if response.status_code not in success_codes:
            print(response.text)
            raise Exception('Invalid status code received. Expected {}. Received {}.'.format(success_codes, response.status_code))
        return response.json()
