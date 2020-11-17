import appdaemon.plugins.hass.hassapi as hass
import time
import pprint
#
# Hellow World App
#
# Args:
#

# tie switches 07 15 16 together

class LightEntity:
    def __init__(self, id, parent):
        self.id = id
        self.parent = parent
        self.brightness = 255

    def __str__(self):
        return self.id

class LightGroup:
    def __init__(self, id):
        self.id = id
        self.locked = False
        self.entities = []
        
    def addEntity(self, id):
        entity = LightEntity(id, self)
        self.entities.append(entity)
        
    def __str__(self):
        s = str(self.id + '\n')
        for entity in self.entities:
            s += ('    Entity: ' + str(entity) + '\n')
        return s

class HelloWorld(hass.Hass):

    def initialize(self):
        self.log("Light Switching App")
        self.listen_event(self.fooEvent, "state_changed")#, entity_id="light.test_1_dimmer_level")
        self.listen_event(self.fooService, "call_service")
        self.raw_groups = self.get_state("group")
        self.groups = {}
        self.all_entities = []
        self.lightGroups = []
        for name, data in self.raw_groups.items():
            self.log(name + ' (' + data['attributes']['friendly_name'] + ')')
            ids = data['attributes']['entity_id']
            lightGroup = LightGroup(name)
            for id in ids:
                self.log('  ' + id)
                lightGroup.addEntity(id)
            self.groups[name] = ids
            self.all_entities += ids
            self.lightGroups.append(lightGroup)
        
        self.log('All Entities:')
        self.log(self.all_entities)
        #self.log(pprint.pprint(self.groups))
        self.log('Initialization Complete')
        #self.run_in(self.timeTest, 5)
        self.info()
        
    def info(self):
        self.log(len(self.lightGroups))
        for group in self.lightGroups:
            self.log('LightGroup:\n' + str(group))
    
    def timeTest(self, arg):
        self.log('end time test')
        self.log(arg)

    def fooEvent(self, event_name, data, kwargs):
        # entity state changed
        if data['entity_id'] not in self.all_entities:
            return
        id = data['entity_id']
        self.log("state_changed event on: " + id)
        #self.log(event_name)
        #self.log(data)
        #self.log(kwargs)
    
        state = data['new_state']['state']
        try:
            dim = data['new_state']['attributes']['brightness']
        except KeyError:
            dim = 0
        #self.log(id)
        #self.log(state)
        #self.log(dim)

    def fooService(self, event_name, data, kwargs):
        # group call service
        if not data['domain'] == 'light':
            return
        id = data['service_data']['entity_id']
        if id not in self.groups.keys():
            return
        self.log("call_service event on: " + id)
        #self.log(data)
        #self.log(kwargs)
