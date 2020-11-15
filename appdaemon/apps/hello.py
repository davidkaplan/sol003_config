import appdaemon.plugins.hass.hassapi as hass

#
# Hellow World App
#
# Args:
#

# tie switches 07 15 16 together

class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Light Switching App")
     #self.listen_state(self.fooState, "light.test_1_dimmer_level")
     #self.listen_state(self.fooState, "light.test02_dimmer_level")
     self.listen_event(self.fooEvent, "state_changed")#, entity_id="light.test_1_dimmer_level")
     self.listen_event(self.fooService, "call_service")
     #self.call_service(self.fooService) #, "light.test02_dimmer_level")
     self.groups = self.get_state("group")
     for group in self.groups.values():
         self.log('Found Group: ' + group['attributes']['friendly_name'])
     #self.log(self.groups)
     #self.log('foo')

# state_changed is an event
# call_service is an event

  def fooState(self, entity, attribute, old, new, kwargs):
    self.log("listen STATE")
    self.log(entity)
    self.log(attribute)
    self.log(old)
    self.log(new)
    self.log(kwargs)
    pass 

  def fooEvent(self, event_name, data, kwargs):
    self.log("listen EVENT")
    #self.log(event_name)
    self.log(data)
    self.log(kwargs)
    id = data['entity_id']
    state = data['new_state']['state']
    try:
        dim = data['new_state']['attributes']['brightness']
    except KeyError:
        dim = 0
    self.log(id)
    self.log(state)
    self.log(dim)
    pass

  def fooService(self, event_name, data, kwargs):
    self.log("listen SERVICE")
    self.log(event_name)
    self.log(data)
    self.log(kwargs)
    pass

# check group state change first
# then check individual entities for changes