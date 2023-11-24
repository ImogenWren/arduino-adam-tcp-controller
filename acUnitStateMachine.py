'''
State Machine Testing
Boilerplate found @:
https://stackoverflow.com/questions/2101961/python-state-machine-design

'''
import time

import time
#print(time.time())

#print(round(time.time()))

import acUnitGlobals as glbs

hw = glbs.acHardware


simulate_hardware = True

class stateMachine(object):
    call = 0 # shared state variable
    last_state = "init"


    def next_state(self, cls):
        self.last_state = self.__class__.__name__
        if (self.__class__.__name__ != cls.__name__):
            print('Transition: %s -> %s' %  (self.__class__.__name__,cls.__name__,))
            self.__class__ = cls



    def show_state(self, i):
        glbs.acUnitState = self.__class__.__name__   #
        #print(f"Current State: {glbs.acUnitState}")     ## NOTE this global variable is automatically written to the global dictionary in the sensors task
        #print(f"Last State: {self.last_state}, Current State: {glbs.acUnitState}")
        if (self.last_state != self.__class__.__name__):
            print('%2d:%2d:      %s' % (self.call,i,self.__class__.__name__))



class init_state(stateMachine):
    __call = 0 # state variable
    def __call__(self):
        # track useage - boilerplate
        self.show_state(self.__call)
        self.call += 1
        self.__call += 1
        #state functions
        error = 0
        if not simulate_hardware:
            error += hw.adamDIO_A.set_all_coils([0, 0, 0, 0, 0, 0, 0, 0])  # direct method setting specific controller coil states
            error += hw.adamDIO_B.set_all_coils([0, 0, 0, 0, 0, 0, 0, 0])  ## All direct hardware calls return 0 if success would like to add errors but leaving for later
            error += hw.adamDIO_A.get_all_coils()
            error += hw.adamDIO_B.get_all_coils()
            error += hw.set_compressor(False)
            error += hw.set_fans(False)
        else:
            print("Simulate: Init Hardware")
        #transition
        if error == 0:
            self.next_state(wait_state)
        else:
            self.next_state(error_state)

class error_state(stateMachine):
    __call = 0  # state variable

    def __call__(self):
        self.show_state(self.__call)
        self.call += 1
        self.__call += 1
        print("Error State")
        glbs.update_error_status(9, "State Machine: Error State") ## Errors are updated into global dictionary
        ## Error state - Turn off all equipment / shut all valves
        hw.adamDIO_A.set_all_coils([0,0,0,0,0,0,0,0])  # direct method setting specific controller coil states
        hw.adamDIO_B.set_all_coils([0,0,0,0,0,0,0,0])  ## All direct hardware calls return 0 if success would like to add errors but leaving for later
        hw.adamDIO_A.get_all_coils()
        hw.adamDIO_B.get_all_coils()
        hw.set_compressor(False)
        hw.set_fans(False)
        # Transition
        # No route from error state - hardware must be manually checked





class wait_state(stateMachine):
    __call = 0
    def __call__(self):
        self.show_state(self.__call)
        self.call +=1
        self.__call +=1

        #transition
        if glbs.command_received:
            glbs.command_received = False
            self.next_state(check_cmd_que)
        else:
            self.next_state(wait_state)



class check_cmd_que(stateMachine):
    __call = 0
    def __call__(self):
        self.show_state(self.__call)
        self.call +=1
        self.__call +=1
        try:
            print(f"Command Queue: {glbs.command_queue}")
            #command = glbs.command_queue[0]              ##I think this line was expecting a list of tuples and instead just has list
            command = glbs.command_queue
            glbs.command_queue = []  # wipe global command queue
        except:
            print("Command Queue Empty but shouldnt be")
            glbs.update_error_status(5, "Command queue empty but shouldnt be")
            raise
        while command:
            if command[0] in glbs.valve_list:
                print(f"SIMULATED {command[0]} is {command[1]} ")
                hw.set_valve_name(command[0], command[1])
            elif command[0] in glbs.fan_names:
                print(f"SIMULATED FANS are {command[1]}")
                hw.set_fans(command[1])
            elif command[0] == glbs.compressor_names:
                print(f"SIMULATED COMPRESSOR is {command[1]}")
                hw.set_compressor(command[1])
            else:
                print("unknown command in command Queue")
                glbs.update_error_status(5, "Unknown Command In Queue")
            del command[0:2]
            #print(f"Last command queue: {command}")  ## Just checks command queue is empty
        #transition
        self.next_state(wait_state)





if __name__ == '__main__':
    sm = init_state()
    loops = 10
    while (loops):
        sm()
        loops -= 1
    print ('---------')
    print( vars(sm))