from models.y_pos import YPos

import time


class HBSOperator:
    """ Operator for a high bay warehouse """
    io = object
    soll_x = 0

    def __init__(self, io_extension):  # expects io_extension as argument
        self.io = io_extension

    def s(self):
        """ Wrapper to call stop_motion faster in the terminal """
        self.stop_motion()

    def stop_motion(self):
        """ Stop any motion of the operator """
        for idx in range(8):
            # port 2 == True does not cause motion
            if idx == 2:
                continue
            self.io.set_port(0, idx, False)
        for idx in range(3):
            self.io.set_port(1, idx, False)

    def slow_motion(self, slow: bool):
        """ Set the slow motion mode True or False """
        self.io.set_port(0, 2, slow)

    def get_xpos(self) -> int:
        """ Get the x-axis position of the operator """
        cnt = 0
        for port in self.io.read_port(0):
            cnt += 1
            if port:
                return cnt
        for port in self.io.read_port(1):
            cnt += 1
            if not cnt <= 10:
                break
            if port:
                return cnt

    def get_ypos(self) -> YPos:
        """ Get the y-axis position of the operator """
        cnt = 0
        for port in self.io.read_port(1)[2:5]:
            if port:
                return YPos(cnt)
            cnt += 1

    def get_zpos(self) -> int:
        """ Return the z-axis position of the operator"""
        ports = self.io.read_port(1)[5:8] + self.io.read_port(2)[0:7]
        ports.reverse()
        cnt = 1
        for port in ports:
            if port:
                return cnt
            cnt += 1

    def move_xzpos(self, target_xpos: int, target_zpos: int):
        """ Move the operator to the z-axis position a_xpos"""
        if not 1 <= target_xpos <= 10:
            print("target_xpos of ", target_xpos, " is not allowed. Only 1 to 10 is allowed.")
            return
        if not self.get_ypos() is YPos.DEFAULT:
            print("operator can't move while YPos is not YPos.DEFAULT")
            return
        if not 1 <= target_zpos <= 10:
            print("target_xpos of ", target_zpos, " is not allowed. Only 1 to 10 is allowed.")
            return

        current_zpos = self.get_zpos()
        current_xpos = self.get_xpos()
        slow_xpos = 0

        if current_xpos == target_xpos and current_zpos == target_zpos:
            return

        if current_xpos < target_xpos:
            self.io.set_port(0, 0, True)
            slow_xpos = -1
        elif current_xpos > target_xpos:
            self.io.set_port(0, 1, True)
            slow_xpos = 1

        if current_zpos < target_zpos:
            self.io.set_port(0, 5, True)
        elif current_zpos > target_zpos:
            self.io.set_port(0, 6, True)

        # polling for 10s
        t_end = time.time() + 10
        while time.time() < t_end:
            # X-axis
            current_xpos = self.get_xpos()
            current_zpos = self.get_zpos()
            if current_xpos == target_xpos + slow_xpos:
                self.slow_motion(True)
            if current_xpos == target_xpos:
                self.io.set_port(0, 0, False)
                self.io.set_port(0, 1, False)
                self.slow_motion(False)
            # Z-axis
            if current_zpos == target_zpos:
                self.io.set_port(0, 5, False)
                self.io.set_port(0, 6, False)

            if current_zpos == target_zpos and current_xpos == target_xpos:
                self.stop_motion()
                return
        self.stop_motion()

    def move_xpos(self, a_xpos: int):
        """ Move the operator to the z-axis position a_xpos"""
        if not 1 <= a_xpos <= 10:
            print("a_xpos of ", a_xpos, " is not allowed. Only 1 to 10 is allowed.")
            return
        if not self.get_ypos() is YPos.DEFAULT:
            print("operator can't move in x-direction while ypos is not YPos.DEFAULT")
            return
        self.soll_x = a_xpos
        l_xpos = self.get_xpos()
        slow_xpos = 0
        if l_xpos == a_xpos:
            return
        if l_xpos < a_xpos:
            self.io.set_port(0, 0, True)
            slow_xpos = -1
        elif l_xpos > a_xpos:
            self.io.set_port(0, 1, True)
            slow_xpos = 1
        # xpos is already at a_xpos
        else:
            return
        # polling for 10s
        t_end = time.time() + 10
        while time.time() < t_end:
            current_xpos = self.get_xpos()
            if current_xpos == a_xpos + slow_xpos:
                self.slow_motion(True)
            if current_xpos == a_xpos:
                # commented out to test stop with interrupts
                # self.stop_motion()
                self.slow_motion(False)
                return
        # commented out to test stop with interrupts
        # self.stop_motion()

    def stop_if_target_reached(self):
        """ Not fully implemented.
        Stops the operator when the target position is reached.
        Currently only with an x_pos check to test interrupts. """
        if self.soll_x == self.get_xpos():
            print("Stop motion interrupt")
            self.stop_motion()

    def move_ypos(self, a_ypos: YPos):
        """ Move the operator to the y-axis position a_ypos"""
        l_ypos = self.get_ypos()

        if l_ypos.value > a_ypos.value:
            self.io.set_port(0, 4, True)
        elif l_ypos.value < a_ypos.value:
            self.io.set_port(0, 3, True)
        # ypos is already at y_xpos
        else:
            return
        # polling for 5s
        t_end = time.time() + 5
        while time.time() < t_end:
            if self.get_ypos() is a_ypos:
                self.stop_motion()
                return
        self.stop_motion()

    def move_zpos(self, target_zpos: int):
        """ Move the operator over/under the z-axis position a_zpos. """
        if not 1 <= target_zpos <= 10:
            print("target_xpos of ", target_zpos, " is not allowed. Only 1 to 10 is allowed.")
            return
        current_zpos = self.get_zpos()

        if target_zpos < current_zpos:
            self.io.set_port(0, 6, True)
        else:
            self.io.set_port(0, 5, True)
        # polling for 10s
        t_end = time.time() + 10
        while time.time() < t_end:
            if target_zpos == self.get_zpos():
                self.stop_motion()
                return
        self.stop_motion()

    def get_new_box(self):
        """ Get a new box from the input-station. """
        try:
        self.move_ypos(YPos.DEFAULT)
        self.move_xzpos(10, 1)
        # Start the input-station
        self.io.set_port(1, 0, True)
        self.io.set_port(1, 2, True)

        # Polling für 5s
        t_end = time.time() + 5
        while time.time() < t_end:
            if not self.io.read_port(3)[1]:
                time.sleep(0.3)
                # Stop the input-station
                self.io.set_port(1, 0, False)
                self.io.set_port(1, 2, False)
                break
        self.move_ypos(YPos.DESTORE)
        self.move_zpos(2)
        self.move_ypos(YPos.DEFAULT)

    def put_box(self, xpos, zpos):
        """ Put box into a storage place. """
        z_over = zpos * 2
        z_under = z_over - 1
        self.move_ypos(YPos.DEFAULT)
        self.move_xzpos(xpos, z_over)
        self.move_ypos(YPos.STORE)
        self.move_zpos(z_under)
        self.move_ypos(YPos.DEFAULT)

    def get_box(self, xpos, zpos):
        """ Get a new box from a storage place. """
        zpos_over = zpos * 2
        zpos_under = zpos_over - 1
        self.move_ypos(YPos.DEFAULT)
        self.move_xzpos(xpos, zpos_under)
        self.move_ypos(YPos.STORE)
        self.move_zpos(zpos_over)
        self.move_ypos(YPos.DEFAULT)

    def drop_box(self):
        """ Put a box into the output-station. """
        self.move_ypos(YPos.DEFAULT)
        self.move_xzpos(1, 2)
        self.move_ypos(YPos.DESTORE)
        self.move_zpos(1)
        self.move_ypos(YPos.DEFAULT)
        # Start the output-station
        self.io.set_port(0, 7, True)
        self.io.set_port(1, 1, True)
        time.sleep(6)
        # Stop the output-station
        self.io.set_port(0, 7, False)
        self.io.set_port(1, 1, False)

    def store_box(self, xpos: int, zpos: int):
        """ Get a new box from the input-station and put it into a storage place. """
        try:
            self.get_new_box()
            self.put_box(xpos, zpos)
        except:
            print("Something went wrong in store_box")
            self.stop_motion()

    def restore_box(self, old_xpos: int, old_zpos: int, xpos: int, zpos: int):
        """ Get a box from a storage place and restore it to another. """
        try:
            self.get_box(old_xpos, old_zpos)
            self.put_box(xpos, zpos)
        except:
            print("Something went wrong in restore_box")
            self.stop_motion()

    def destore_box(self, xpos: int, zpos: int):
        """ Get a box from a storage place and put it into the output-station. """
        try:
            self.get_box(xpos, zpos)
            self.drop_box()
        except:
            print("Something went wrong in destore_box")
            self.stop_motion()

    def show(self, xpos1: int, zpos1: int, xpos2: int, zpos2: int):
        """ Show the HBSOperator functionality. """
        self.store_box(xpos1, zpos1)
        time.sleep(1)
        self.restore_box(xpos1, zpos1, xpos2, zpos2)
        time.sleep(1)
        self.destore_box(xpos2, zpos2)
