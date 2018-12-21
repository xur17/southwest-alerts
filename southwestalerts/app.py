import locale
locale.resetlocale()
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
            try:
                cancellation_details = southwest.get_cancellation_details(record_locator, passenger['firstName'], passenger['lastName'])
                itinerary_price = cancellation_details['pointsRefund']['amountPoints']
                itinerary_price = int(itinerary_price/len(cancellation_details['passengers'])) # support multi-passenger itineraries
            except:
                print("Caught error from revenue or international trip")
                continue
            # Calculate total for all of the legs of the flight
            matching_flights_price = 0
            logging.info('itinerary original total price: %s',itinerary_price)
            for origination_destination in cancellation_details['itinerary']['originationDestinations']:
                departure_datetime = origination_destination['segments'][0]['departureDateTime'].split('.000')[0][:-3]
                departure_date = departure_datetime.split('T')[0]
                departure_time = departure_datetime.split('T')[1]
                arrival_datetime = origination_destination['segments'][-1]['arrivalDateTime'].split('.000')[0][:-3]
                arrival_time = arrival_datetime.split('T')[1]

                origin_airport = origination_destination['segments'][0]['originationAirportCode']
                destination_airport = origination_destination['segments'][-1]['destinationAirportCode']
                available = southwest.get_available_flights(
                    departure_date,
                    origin_airport,
                    destination_airport
                )

                # Find that the flight that matches the purchased flight
                matching_flight = next(f for f in available['flightShoppingPage']['outboundPage']['cards'] if f['departureTime'] == departure_time and f['arrivalTime'] == arrival_time)
                for faretype,fare in enumerate(matching_flight['fares']):
                        logging.info('current leg faretype %d price: %s',faretype,fare['price'])
                        # Check to make sure the flight isnt sold out to avoid NoneType object is not subscriptable error
                        if fare['price'] is None:
                            logging.info("fare type %d is sold out",faretype)
                            #if fare type is sold out, then use next rate for calculations, so let this for loop continue
                        else:
                            matching_flight_price = locale.atoi(matching_flight['fares'][faretype]['price']['amount'])
                            #if fare type isn't sold out, then set the price and break out of the faretype loop.
                            break
                    
                matching_flights_price += matching_flight_price

            # Calculate refund details (current flight price - sum(current price of all legs), and print log message
            refund_amount = itinerary_price - matching_flights_price
            if matching_flights_price == 0:
                base_message='(unavailable) 0'
            else:
                base_message='Price drop of {}'.format(refund_amount) if refund_amount > 0 else 'Price increase of {}'.format(refund_amount * -1)
            message = '{base_message} points detected for flight {record_locator} from {origin_airport} to {destination_airport} on {departure_date}'.format(
                base_message=base_message,
                refund_amount=refund_amount,
                record_locator=record_locator,
                origin_airport=origin_airport,
                destination_airport=destination_airport,
                departure_date=departure_date
            )
            logging.info(message)
            if matching_flights_price > 0 and refund_amount > 0:
                logging.info('Sending email for price drop')
                resp = requests.post(
                    'https://api.mailgun.net/v3/{}/messages'.format(settings.mailgun_domain),
                    auth=('api', settings.mailgun_api_key),
                    data={'from': 'Southwest Alerts <southwest-alerts@{}>'.format(settings.mailgun_domain),
                          'to': [email],
                          'subject': 'Southwest Price Drop Alert',
                          'text': message})
                assert resp.status_code == 200


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    for user in settings.users:
        check_for_price_drops(user.username, user.password, user.email)
