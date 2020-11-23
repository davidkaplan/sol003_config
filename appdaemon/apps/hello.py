import appdaemon.plugins.hass.hassapi as hass
import time
import pprint
import datetime
#
# Hellow World App
#
# Args:
#

# tie switches 07 15 16 together

_TIMEOUT = 5

class LightEntity:
    def __init__(self, id, hassObj, parent=None):
        self.id = id
        self.hassObj = hassObj
        self.parent = parent
        self.brightness = (self.hassObj).get_state(entity_id=id, attribute='brightness')
        #self._locked = False
        self.time = datetime.datetime.now()

    def isSynced(self):
        return (self.brightness == self.get_state(entity_id=self.id, attribute='brightness'))

    def setCurrentTime(self):
        self.time = datetime.datetime.now()

    def isTimedOut(self):
        seconds = (datetime.datetime.now() - self.time).total_seconds()
        if seconds >= _TIMEOUT:
            self.log('WARNING Timeout reached waiting for light to reach target value')
            return True
        else:
            return False

    def turnOn(self, brightness):
        if brightness is None:
            self.turn_on(self.id)
        else:
            self.turn_on(self.id, brightness=brightness)

    def turnOff(self):
        self.turn_off(self.id)

    # def isLocked(self):
    #     return self._locked
        
    # def lock(self):
    #     self._locked = True
        
    # def unlock(self):
    #     self._locked = False

    def __str__(self):
        return self.id

class LightGroup(LightEntity):
    def __init__(self, id, hassObj):
        super().__init__(id, hassObj)
        #self.id = id
        #self._locked = False
        #self.brightness = 255
        self.entities = []

    def addEntity(self, id):
        entity = LightEntity(id, self.hassObj)
        self.entities.append(entity)
        
    def isSynced(self):
        #if not super().isSynced():
        #    return False
        for entity in self.entities:
            if not entity.isSynced():
                return False
        return True

    def hasEntity(self, id):
        for entity in self.entities:
            if entity.id == id:
                return True
        return False
        
    # def lock(self):
    #     super().lock()
    #     for entity in self.entities:
    #         entity.lock()
        
    # def unlock(self):
    #     super().unlock()
    #     for entity in self.entities:
    #         entity.unlock()

    def __len__(self):
        return len(self.entities)

    def __iter__(self):
        return iter(self.entities)
    
    def __str__(self):
        s = str(self.id + '\n')
        for entity in self.entities:
            s += ('    Entity: ' + str(entity) + '\n')
        return s

class LightGroups:
    def __init__(self):
        self.lightGroups = []
        self.allEntityNames = []

    def addGroup(self, group):
        self.lightGroups.append(group)
        self.allEntityNames += [x.id for x in group.entities]

    def getAllEntities(self):
        return self.allEntityNames

    def getGroupByEntity(self, id):
        for group in self.lightGroups:
            if group.hasEntity(id):
                return group
        return None

    def getEntity(self, id):
        for group in self.lightGroups:
            for entity in group:
                if entity.id == id:
                    return entity
        return None

    def __len__(self):
        return len(self.lightGroups)

    def __iter__(self):
        return iter(self.lightGroups)


class HelloWorld(hass.Hass):

    def initialize(self):
        self.log("Light Switching App")
        self.listen_event(self.handleStateChange, "state_changed")#, entity_id="light.test_1_dimmer_level")
        self.listen_event(self.handleCallService, "call_service")
        self.raw_groups = self.get_state("group")
        self.lightGroups = LightGroups()



        #self.groups = {}
        #self.all_entities = []
        #self.lightGroups = []
        for name, data in self.raw_groups.items():
            self.log(name + ' (' + data['attributes']['friendly_name'] + ')')
            ids = data['attributes']['entity_id']
            lightGroup = LightGroup(name, self)
            for id in ids:
                self.log('  ' + id)
                lightGroup.addEntity(id)
            #self.groups[name] = ids
            #self.all_entities += ids
            self.lightGroups.addGroup(lightGroup)
        
        self.log('All Entities:')
        self.log(self.lightGroups.getAllEntities())
        #self.log(pprint.pprint(self.groups))
        self.log('Initialization Complete')
        #self.run_in(self.timeTest, 5)
        self.info()
        
    def info(self):
        self.log(len(self.lightGroups))
        for group in self.lightGroups:
            self.log('LightGroup:\n' + str(group))
    
    # def timeTest(self, arg):
    #     self.log('end time test')
    #     self.log(arg)
        
    # def checkBrightness(self, entity, target):
    #     b = self.get_state(entity_id=entity, attribute='brightness')
    #     self.log('checkBrightness entity ' + entity + ' ' + str(b))
    #     return (b == target)

    def handleStateChange(self, event_name, data, kwargs):
        # entity state changed
        if data['entity_id'] not in self.lightGroups.getAllEntities():
            return
        id = data['entity_id']
        self.log("state_changed event on: " + id)
        #self.log(event_name)
        #self.log(data)
        #self.log(kwargs)
    
        state = data['new_state']['state'] # 'on' or 'off'
        try:
            target_brightness = data['new_state']['attributes']['brightness']
        except KeyError:
            target_brightness = 0

        # Make sure it's been a few seconds since entity's last state change
        entity = self.lightGroups.getEntity(id)
        if not entity.isTimedOut():
            return

        group = self.lightGroups.getGroupByEntity(id)
        id = group.id

        self.log('light parent is: ' + id)

        # 
        if target_brigtness == group.brightness:
            return

        if not group.isTimedOut():
            return



        if state == 'off':
            self.turnOff(id)
        elif state == 'on':
            self.turnOn(id, target_brightness)

        # get parent light group of entity
        # service call set brightness on light group
        # set target brightness on group and all child entity objects
        # reset timeout time
        #
        #
        # current = data['old_state']['attributes']['brightness']
        # i = 0
        # self.log('Target: ' + str(target_brightness))
        # while True:
        #     self.log(str(i) + ' brightness: ' + str(current))
        #     if target_brightness == current:
        #         break
        #     current = self.get_state(entity_id=id, attribute='brightness')
        #     i += 1
        #     if i > 2000:
        #         self.log('DEBUG: Reached endless loop')
        #         break


    def handleCallService(self, event_name, data, kwargs):
        # group call service
        if not data['domain'] == 'light':
            return
        id = data['service_data']['entity_id']
        if id not in self.lightGroups.getAllEntities():
            return
        self.log("call_service event on: " + id)
        service = data['service'] # 'turn_on' or 'turn_off'
        brightness = 0
        if service == 'turn_off':
            self.turnOff(id)
        if service == 'turn_on':
            brightness = data['service_data']['brightness_pct']
            self.turnOn(id, brightness)

        #self.log(data)
        #self.log(kwargs)

    def turnOff(self, id):
        pass

    def turnOn(self, id):
        pass
