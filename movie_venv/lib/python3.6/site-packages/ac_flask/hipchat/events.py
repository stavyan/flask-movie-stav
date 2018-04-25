import logging

_log = logging.getLogger(__name__)


class EventBus(object):

    def __init__(self):
        super(EventBus, self).__init__()
        self.events = {}

    def fire_event(self, name, obj):
        listeners = self.events.get(name, [])
        _log.debug("Firing event %s for %s listeners" % (name, len(listeners)))
        for listener in listeners:
            listener(obj)

    def register_event(self, name, func):
        _log.debug("Registering event: " + name)
        self.events.setdefault(name, []).append(func)

    def unregister_event(self, name, func):
        del self.events.setdefault(name, [])[func]

    def event_listener(self, func):
        self.register_event(func.__name__, func)
        return func

events = EventBus()