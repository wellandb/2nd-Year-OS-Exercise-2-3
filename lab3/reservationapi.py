""" Reservation API wrapper

This class implements a simple wrapper around the reservation API. It
provides automatic retries for server-side errors, delays to prevent
server overloading, and produces sensible exceptions for the different
types of client-side error that can be encountered.
"""

# This file contains areas that need to be filled in with your own
# implementation code. They are marked with "Your code goes here".
# Comments are included to provide hints about what you should do.

import http
from msilib.schema import IniFile
from urllib import request
import requests
import simplejson
import warnings
import time

from requests.exceptions import HTTPError
from exceptions import (
    BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
    SlotUnavailableError,ReservationLimitError)

class ReservationApi:
    def __init__(self, base_url: str, token: str, retries: int, delay: float):
        """ Create a new ReservationApi to communicate with a reservation
        server.

        Args:
            base_url: The URL of the reservation API to communicate with.
            token: The user's API token obtained from the control panel.
            retries: The maximum number of attempts to make for each request.
            delay: A delay to apply to each request to prevent server overload.
        """
        self.base_url = base_url
        self.token    = token
        self.retries  = retries
        self.delay    = delay

    def _reason(self, req: requests.Response) -> str:
        """Obtain the reason associated with a response"""
        reason = ''

        # Try to get the JSON content, if possible, as that may contain a
        # more useful message than the status line reason
        try:
            json = req.json()
            reason = json['message']

        # A problem occurred while parsing the body - possibly no message
        # in the body (which can happen if the API really does 500,
        # rather than generating a "fake" 500), so fall back on the HTTP
        # status line reason
        except simplejson.errors.JSONDecodeError:
            if isinstance(req.reason, bytes):
                try:
                    reason = req.reason.decode('utf-8')
                except UnicodeDecodeError:
                    reason = req.reason.decode('iso-8859-1')
            else:
                reason = req.reason

        return reason


    def _headers(self) -> dict:
        """Create the authorization token header needed for API requests"""
        # Your code goes here
        self.bandAPI = "Authorization: Bearer 78c957b75b2bcf20796bf3da62b1ed5769e2edb02bd120c8767579ecca0084f4"
        self.hotelAPI = "Authorization: Bearer 48e3b27f6113ebddfea90d4fa9119bc90066f982c1425b6dcd0d8a2d09d8f259"


    def _send_request(self, method: str, endpoint: str) -> dict:
        """Send a request to the reservation API and convert errors to
           appropriate exceptions"""
        # Your code goes here
        requestConfirm = False

        # Allow for multiple retries if needed
        while not(requestConfirm):
            # Perform the request.
            match method:
                case "get_slots_available()":
                    response = self.get_slots_available()
                case "get_slots_held()":
                    response = self.get_slots_held()
                case method.startswith("release_slot"):
                    response = self.release_slot(int(method[method.find("(") + 1:len(method)-1]))
                case method.startswith("reserve_slot"):
                    response = self.reserve_slot(int(method[method.find("(") + 1:len(method)-1]))
                
            
            # Delay before processing the response to avoid swamping server.
            time.sleep(1)

            # Get data from response
            data = response.json()
            code = data["code"]

            # 200 response indicates all is well - send back the json data.
            if code == 200:
                request.post(url=endpoint,data=code)

            # 5xx codes indicate a server-side error, show a warning
            # (including the try number).
            elif code.startswith(5) and len(code) == 3:
                print("Warning, server side error. Error:", str(code))

            # 400 errors are client problems that are meaningful, so convert
            # them to separate exceptions that can be caught and handled by
            # the caller.
            elif code.startswith(4) and len(code) == 3:
                if code == 400:
                    # throws BadRequestError
                    pass
                # 401 error
                elif code == 401:
                    pass
                    # class InvalidTokenError(RequestException):

                # 403 error
                elif code == 403:
                    pass
                    # class BadSlotError(RequestException):

                # 404 error
                elif code == 404:
                    pass
                    # class NotProcessedError(RequestException):

                # 409 error
                elif code == 409:
                    pass
                    # class SlotUnavailableError(RequestException):

                # 451 error
                elif code == 451:
                    pass
                    # class ReservationLimitError(RequestException):

            # Anything else is unexpected and may need to kill the client.
            else:
                # Freak out
                pass

            count += 1
            if count == self.retries:
                # Throw ReservationLimitError
                break

        # Get here and retries have been exhausted, throw an appropriate
        # exception.


    def get_slots_available(self):
        """Obtain the list of slots currently available in the system"""
        # Your code goes here
        return requests.get(url="https://web.cs.manchester.ac.uk/hotel/api/reservation")

    def get_slots_held(self):
        """Obtain the list of slots currently held by the client"""
        # Your code goes here
        return requests.get(url="https://web.cs.manchester.ac.uk/hotel/api/reservation/available")

    def release_slot(self, slot_id):
        """Release a slot currently held by the client"""
        # Your code goes here
        return requests.delete(url="https://web.cs.manchester.ac.uk/hotel/api/reservation/" + str(slot_id))

    def reserve_slot(self, slot_id):
        """Attempt to reserve a slot for the client"""
        # Your code goes here
        return requests.post(url="https://web.cs.manchester.ac.uk/hotel/api/reservation/" + str(slot_id))
