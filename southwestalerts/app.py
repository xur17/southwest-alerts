import logging
import requests
import sys

from southwestalerts.southwest import Southwest
from southwestalerts import settings


def check_for_price_drops(username, password, email):
    southwest = Southwest(username, password)
    for trip in southwest.get_upcoming_trips()['trips']:
        for flight in trip['flights']:
            passenger = flight['passengers'][0]
            record_locator = flight['recordLocator']
            itinerary = southwest.start_change_flight(record_locator, passenger['firstName'], passenger['lastName'])['itinerary']
            for originination_destination in itinerary['originationDestinations']:
                departure_datetime = originination_destination['segments'][0]['departureDateTime'].split('.000')[0][:-3]
                departure_date = departure_datetime.split('T')[0]
                arrival_datetime = originination_destination['segments'][-1]['arrivalDateTime'].split('.000')[0][:-3]

                origin_airport = originination_destination['segments'][0]['originationAirportCode']
                destination_airport = originination_destination['segments'][-1]['destinationAirportCode']
                available = southwest.get_available_change_flights(
                    record_locator,
                    passenger['firstName'],
                    passenger['lastName'],
                    departure_date,
                    origin_airport,
                    destination_airport
                )

                # Find that the flight that matches the purchased flight
                matching_flight = next(f for f in available['trips'][0]['airProducts'] if f['segments'][0]['departureDateTime'] == departure_datetime and f['segments'][-1]['arrivalDateTime'] == arrival_datetime)
                product_id = matching_flight['fareProducts'][-1]['productId']
                refund_details = southwest.get_price_change_flight(record_locator, passenger['firstName'], passenger['lastName'], product_id)['pointsDifference']
                message = '{base_message} points detected for flight {record_locator} from {origin_airport} to {destination_airport} on {departure_date}'.format(
                    base_message='Price drop of {}'.format(refund_details['refundAmount']) if refund_details['refundAmount'] > 0 else 'Price increase of {}'.format(refund_details['amountDue']),
                    refund_amount=refund_details['refundAmount'],
                    record_locator=record_locator,
                    origin_airport=origin_airport,
                    destination_airport=destination_airport,
                    departure_date=departure_date,
                )
                logging.info(message)
                if refund_details['refundAmount'] > 0:
                    logging.info('Sending email for price drop')
                    resp = requests.post(
                        'https://api.mailgun.net/v3/tdickman.mailgun.org/messages',
                        auth=('api', settings.mailgun_api_key),
                        data={'from': 'Southwest Alerts <southwest-alerts@tdickman.mailgun.org>',
                              'to': [email],
                              'subject': 'Southwest Price Drop Alert',
                              'text': message})
                    assert resp.status_code == 200


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    for user in settings.users:
        check_for_price_drops(user.username, user.password, user.email)
