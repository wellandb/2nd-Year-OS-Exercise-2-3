""" Reservation API wrapper

This class implements a simple wrapper around the reservation API. It
provides automatic retries for server-side errors, delays to prevent
server overloading, and produces sensible exceptions for the different
types of client-side error that can be encountered.
"""

# This file contains areas that need to be filled in with your own
# implementation code. They are marked with "Your code goes here".
# Comments are included to provide hints about what you should do.

from urllib import request
import requests
import simplejson
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
        return {"Authorization": f"Bearer {self.token}"}


    def _send_request(self, method: str, endpoint: str) -> dict:
        """Send a request to the reservation API and convert errors to
           appropriate exceptions"""
        # Your code goes here
        requestConfirm = False
        count = 0

        # Allow for multiple retries if needed
        while not(requestConfirm):
            # Perform the request.
            
            if method == "GET":
                response = requests.get(url=f'{endpoint}', headers=self._headers())
            elif method == "DEL":
                response = requests.delete(url=f'{endpoint}', headers=self._headers())
            elif method == "POST":
                response = requests.post(url=f'{endpoint}', headers=self._headers())
            else:
                print("Method not found.")
                break
                
            
            # Delay before processing the response to avoid swamping server.
            time.sleep(self.delay)

            # Get data from response
            data = response.json()
            code = response.status_code

            # 200 response indicates all is well - send back the json data.
            try:
                if code == 200:
                    requestConfirm = True
                    return data

                # 5xx codes indicate a server-side error, show a warning
                # (including the try number).
                elif code == 503:
                    print(f"Service unavailable. Error: {code}")
                elif str(code)[0] == "5" and len(str(code)) == 3:
                    print(f"Warning, server side error. Error: {code}")

                # 400 errors are client problems that are meaningful, so convert
                # them to separate exceptions that can be caught and handled by
                # the caller.
                elif code == 400:
                    raise BadRequestError("")
                # 401 error
                elif code == 401:
                    raise InvalidTokenError("")

                # 403 error
                elif code == 403:
                    raise BadSlotError("")

                # 404 error
                elif code == 404:
                    raise NotProcessedError("")

                # 409 error
                elif code == 409:
                    raise SlotUnavailableError("")

                # 451 error
                elif code == 451:
                    raise ReservationLimitError("")

                # Anything else is unexpected and may need to kill the client.
                else:
                    # Freak out
                    print("Unexpected code:", str(code))
                    quit()

            except BadRequestError:
                print("400 Error: Bad Request")
            except InvalidTokenError:
                print("401 Error: Invalid Token")
                quit()
            except BadSlotError:
                print("403 Error: Bad Slot")
                continue
            except NotProcessedError:
                print("404 Error: Not Processed")
                continue
            except SlotUnavailableError:
                print("409 Error: Slot Unavailable")
                return "409 Error"
            except ReservationLimitError:
                print("451 Error: Reservation Limit Reached")
                self.release_slot(max(self.get_slots_held()))


            count += 1
            if count == self.retries:
                print("Method has failed, too many retries")
                quit()

        # Get here and retries have been exhausted, throw an appropriate
        # exception.


    def get_slots_available(self):
        """Obtain the list of slots currently available in the system"""
        # Your code goes here
        available = []
        res = self._send_request("GET", f"{self.base_url}/reservation/available")
        for slots in res:
            available.append(slots["id"])
        return available
        
    def get_slots_held(self):
        """Obtain the list of slots currently held by the client"""
        # Your code goes here
        held = []
        response = self._send_request("GET", f"{self.base_url}/reservation")
        for slots in response:
            held.append(slots["id"])
        return held

    def release_slot(self, slot_id):
        """Release a slot currently held by the client"""
        # Your code goes here
        return self._send_request("DEL", f"{self.base_url}/reservation/{slot_id}")

    def reserve_slot(self, slot_id):
        """Attempt to reserve a slot for the client"""
        # Your code goes here
        return self._send_request("POST", f"{self.base_url}/reservation/{slot_id}")
