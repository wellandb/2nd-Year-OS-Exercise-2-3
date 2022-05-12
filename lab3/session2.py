#!/usr/bin/python3

import time
import reservationapi
import configparser

# Load the configuration file containing the URLs and keys
config = configparser.ConfigParser()
config.read("api.ini")

# Create an API object to communicate with the band API
hotel  = reservationapi.ReservationApi(config['hotel']['url'],
                                       config['hotel']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))

band  = reservationapi.ReservationApi(config['band']['url'],
                                       config['band']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))

# Your code goes here
checks = 3

for i in range(checks):
    hotelHold = hotel.get_slots_held()
    bandHold = band.get_slots_held()

    if len(hotelHold) == 0 and len(bandHold) > 0:
        for slot in bandHold:
            band.release_slot(slot)
    elif len(hotelHold) > 0 and len(bandHold) == 0:
        for slot in hotelHold:
            hotel.release_slot(slot)
    else:
        for slot in hotelHold:
            if slot not in bandHold:
                band.release_slot(slot)
        for slot in bandHold:
            if slot not in hotelHold:
                hotel.release_slot(slot)

    print("Searching for slots")

    slotFound = False
    while not slotFound:
        hotelAvailable = hotel.get_slots_available()
        bandAvailable = band.get_slots_available()

        commonFound = False
        hotelSlot = 0
        bandSlot = 0
        
        for slot in hotelAvailable: 
            if slot in bandAvailable:
                bestH = hotel.reserve_slot(hotelAvailable[slot])
                bestB = band.reserve_slot(bandAvailable[slot])
                reserveSlot = slot
                break
        
        if hotelHold[0] < reserveSlot:
            hotel.release_slot(bestH)
            band.release_slot(bestB)
            hotelHold.remove(bestH)
            bandHold.remove(bestB)
            bestH = hotelHold[0]
            bestB = bandHold[0]
                

        if bestB == "409 Error":
            hotel.release_slot(bestH)
        elif bestH == "409 Error":
            band.release_slot(bestB)
        else:
            slotFound == True
        
        time.delay(1)

    print(f"Slot {bestH} reserved for the hotel")
    print(f"Slot {bestB} reserved for the band")

    if i < checks - 1:
        print ("Checking Again")

print("Slots found: ")
print(f"Hotel: Slot {bestH}")
print(f"Band: Slot {bestB}")
