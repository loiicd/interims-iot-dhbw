from pathlib import Path

import random
import pickle
import time


class HighBayStorage:
    """class for storage-management of high-bay storage"""
    storage_places = {}     # two-dimensional dictionary [1..50] with keys 'x', 'z', 'taken', 'timestamp'
                            # 'taken': False - place is empty
                            # 'taken': True - place is taken
    op = object     # hbs_operator object

    def __init__(self, operator):       # expects hbs_operator as argument
        self.op = operator              # saves operator as static class element
        if Path('./obj/storage_places_new.pkl').is_file():   # check if file exists
            try:                                                        # try to load file
                self.load_from_file()                                   #
                self.print_all()                                      # optional: print all file entries in terminal

            except:                             # file exists but is not loadable
                print("Could not load data")    # print error message in terminal
        else:   # file does not exist (e.g. first start ) -> prepare storage_places dict and save to file
            x_pos = 1
            z_pos = 1
            for box_nr in range(1, 51):     # from 1 to 50
                if x_pos > 10:              # 10 places on x-axis
                    x_pos = 1
                    z_pos += 1
                self.storage_places[box_nr] = {'x': x_pos, 'z': z_pos, 'taken': False, 'timestamp': None}
                x_pos += 1
            self.save_to_file()             # save
            self.print_all()              # optional: print all file entries in terminal

    def occupy_place(self, place_nr):
        """ change box-status taken on 'true' and save timestamp"""
        self.storage_places[place_nr]['taken'] = True
        self.storage_places[place_nr]['timestamp'] = time.time()
        self.save_to_file()

    def clear_place(self, place_nr):
        """ change box-status taken on 'false' and remove timestamp"""
        self.storage_places[place_nr]['taken'] = False
        self.storage_places[place_nr]['timestamp'] = None
        self.save_to_file() 

    def store_box(self, x_pos, z_pos):
        """get new box from io-station 1 & put box in storage place (x,z)"""
        for key, value in self.storage_places.items():
            if value['x'] == x_pos and value['z'] == z_pos:
                try:
                    self.op.store_box(x_pos, z_pos)
                    self.occupy_place(key)
                    return
                except:
                    print("ooops, something went wrong!")

    def destore_box(self, x_pos, z_pos):
        """get box from storage place (x,z) & put box io-station 2"""
        for key, value in self.storage_places.items():
            if value['x'] == x_pos and value['z'] == z_pos:
                try:
                    self.op.destore_box(x_pos, z_pos)
                    self.clear_place(key)
                    return
                except:
                    print("ooops, something went wrong!")

    def rearrange_box(self, old_xpos, old_zpos, xpos, zpos):
        """get box from (old_xpos, old_zpo) & put box in (xpos, zpos)"""
        for key, value in self.storage_places.items():
            if value['x'] == old_xpos and value['z'] == old_zpos:
                try:
                    self.op.get_box(old_xpos, old_zpos)
                    self.clear_place(key)
                    break
                except:
                    print("ooops, something went wrong!")

        for key, value in self.storage_places.items():
            if value['x'] == xpos and value['z'] == zpos:
                try:
                    self.op.put_box(xpos, zpos)
                    self.occupy_place(key)
                    return
                except:
                    print("ooops, something went wrong!")

    def store_box_ascending(self):
        """Puts box in first free storage place ascending"""
        if not self.hbs_is_full():    # check if at least one free place is available
            for box_nr in range(1, 51):  # from 1 to 51
                if not self.storage_places[box_nr]['taken']:
                    try:
                        self.op.store_box(self.storage_places[box_nr]['x'], self.storage_places[box_nr]['z'])
                        self.occupy_place(box_nr)
                        return
                    except Exception as e:
                        print(f'Error at store_box_ascending: {e}')

    def destore_box_ascending(self):
        """Destores box from first free storage place ascending"""
        if self.hbs_is_not_empty():     # check if at least one box is stored
            for box_nr in range(1, 51):  # from 1 to 51
                if self.storage_places[box_nr]['taken']:
                    try:
                        self.op.destore_box(self.storage_places[box_nr]['x'],
                                            self.storage_places[box_nr]['z'])
                        self.clear_place(box_nr)
                        return
                    except:
                        print("ooops, something went wrong!")

    def store_box_random(self):
        """Puts box in random storage place"""
        if not self.hbs_is_full():    # check if at least one free place is available
            place_found = False
            while not place_found:
                box_nr_random = random.randrange(1, 51)
                if not self.storage_places[box_nr_random]['taken']:
                    try:
                        self.op.store_box(self.storage_places[box_nr_random]['x'],
                                          self.storage_places[box_nr_random]['z'])
                        self.occupy_place(box_nr_random)
                        place_found = True
                    except:
                        print("ooops, something went wrong!")

    def destore_box_random(self):
        """Destores box from random storage place"""
        if self.hbs_is_not_empty():     # check if at least one box is stored
            place_found = False
            while not place_found:
                box_nr_random = random.randrange(1, 51)
                if self.storage_places[box_nr_random]['taken']:
                    try:
                        self.op.destore_box(self.storage_places[box_nr_random]['x'],
                                            self.storage_places[box_nr_random]['z'])
                        self.clear_place(box_nr_random)
                        place_found = True
                    except:
                        print("ooops, something went wrong!")
                    
    def destore_oldest(self):
        """Destores box with oldest/ lowest timestamp"""
        if self.hbs_is_not_empty():     # check if at least one box is stored
            # find oldest box by timestamp
            oldest_box_nr = min(self.storage_places, key=lambda x: self.storage_places[x]['timestamp']
                                if (self.storage_places[x]['timestamp'] is not None) else 9999999999)
            if self.storage_places[oldest_box_nr]['taken']:
                try:
                    self.op.destore_box(self.storage_places[oldest_box_nr]['x'],
                                                self.storage_places[oldest_box_nr]['z'])
                    self.clear_place(oldest_box_nr)
                except:
                    print("ooops, something went wrong!")
            else:
                print("ooops, something went wrong! Maybe no Box is stored?")

    def hbs_is_full(self) -> bool:
        """returns True if high-bay storage is completely full"""
        for x in self.storage_places:
            if not self.storage_places[x]['taken']:
                return False
        return True

    def hbs_is_not_empty(self) -> bool:
        """returns True if at least one box is stored in high-bay storage"""
        for x in self.storage_places:
            if self.storage_places[x]['taken']:
                return True
        return False

    def save_to_file(self):
        """writes storage_places dict into file"""
        with open('/home/pi/iot/obj/storage_places_new.pkl', 'wb') as f:
            pickle.dump(self.storage_places, f, pickle.HIGHEST_PROTOCOL)

    def load_from_file(self):
        """read storage_places dict from file"""
        with open('/home/pi/iot/obj/storage_places_new.pkl', 'rb') as f:
            self.storage_places = pickle.load(f)
            
    def print_all(self):
        with open('/home/pi/iot/obj/storage_places_new.pkl', 'rb') as f:
            self.storage_places = pickle.load(f)
            print(self.storage_places)