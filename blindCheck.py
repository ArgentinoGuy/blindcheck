#Modified version of CaptCharmander <https://github.com/jasondinh/CaptCharmander/> to check for account warnings

#!/usr/bin/python
# -*- coding: utf-8 -*-

from pgoapi import PGoApi
from pgoapi.utilities import get_cell_ids
import time
import random
import sys
import csv

usernames = []
passwords = []

#Use terminal/cmd or put hash key here
hashKey = None

lat = None
lng = None
pkmnId = None
expireTs = None

def parse_csv():
  try:
    with open('account.csv', 'r') as csvfile:
      data = csv.reader(csvfile, delimiter=',')
      for row in data:
        if len(row) == 2:
          usernames.append(row[0])
          passwords.append(row[1])
  except:
    print("Error opening account.csv, does it exist?")
    sys.exit()

def getStuff():
  global hashKey
  global lat
  global lng
  global pkmnId
  global expireTs
  if not hashKey:
    hashKey = raw_input("Pokehash key: ")
  lat = float(raw_input("Latitude: "))
  lng = float(raw_input("Longitude: "))
  pkmnId = int(raw_input("Pokemon ID to check for: "))
  sec = int(raw_input("Seconds until despawn: "))
  expireTs = int(time.time()) + sec

def write_to_file(filename, username, password):
  with open(filename, "a") as my_file:
    my_file.write("{},{}\n".format(username, password))

def check_account(username, password, count):
  if(int(time.time()) < expireTs - 10):
    if count < 3:
      try:
        print("Trying to login with {}".format(username))
        increment = 0
        api = PGoApi()
        api.activate_hash_server(hashKey)
        api.set_position(lat, lng, random.randrange(3,170))
        api.login("ptc", username, password, False)
        #For app_simulation_login in case
        request = self.create_request()
        request.get_player()
        request.get_hatched_eggs()
        request.get_inventory()
        request.check_awarded_badges()
        request.download_settings(hash="54b359c97e46900f87211ef6e6dd0b7f2a3ea1f5")
        response = request.call()
        time.sleep(10)
        #Checking portion
        req = api.create_request()
        cell_ids = get_cell_ids(lat, lng, radius=70)
        timestamps = [0, ] * len(cell_ids)
        req.get_map_objects(latitude=lat, longitude=lng, cell_id=cell_ids, since_timestamp_ms=timestamps)
        req.check_challenge()
        req.get_hatched_eggs()
        req.get_inventory()
        req.check_awarded_badges()
        req.download_settings()
        req.get_buddy_walked()
        response = req.call()
        #Check if pokemon there
        cells = response['responses']['GET_MAP_OBJECTS']['map_cells']
        if sum(len(cell.keys()) for cell in cells) == len(cells) * 2:
          print("No pokemon found, account may have passed the speed limit or was rate limited")
        else:
          count = 0
          for cell in cells:
            for pokemons in cell.get('wild_pokemon', []):
              if(pokemons['pokemon_id'] == pkmnId):
                count += 1
            for pokemons in cell.get('nearby_pokemons', []):
              if(pokemons['pokemon_id'] == pkmnId):
                count += 1
          print("Found {} of the specified ID".format(count))
          if(count > 0):
            print("{} is clean".format(username))
            write_to_file("clean.csv", username, password)
          else:
            print("{} may be blinded".format(username))
            write_to_file("blinded.csv", username, password)
      except (KeyboardInterrupt, SystemExit):
        sys.exit()
      except Exception as e:
        print(e)
        print("Cannot login with {}, trying again".format(username))
        check_account(username, password, count + 1)
    else:
      print("{} failed to login".format(username))
  else:
    print("Stopped due to pokemon expiration")
    sys.exit()

parse_csv()
getStuff()

def run():
  for i in range(0, len(usernames)):
    username = usernames[i]
    password = passwords[i]
    check_account(username, password, 0)
    print("")
run()
