from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import eEPGCache, eServiceReference
from time import localtime, strftime, mktime, time
from datetime import datetime, timedelta

class SphereFHDEventList(Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)
        self.epgcache = eEPGCache.getInstance()
        self.primetime = 0
        self.eventcount = 0
        if len(type):
            args = type.split(',')
            i = 0
            while i <= len(args) - 1:
                type_c, value = args[i].split('=')
                if type_c == 'eventcount':
                    self.eventcount = int(value)
                elif type_c == 'primetime':
                    if value == 'yes':
                        self.primetime = 1
                i += 1

    @cached
    def getContent(self):
        contentList = []
        ref = self.source.service
        info = ref and self.source.info
        if info is None:
            return []
        else:
            curEvent = self.source.getCurrentEvent()
            if curEvent:
                if not self.epgcache.startTimeQuery(eServiceReference(ref.toString()), curEvent.getBeginTime() + curEvent.getDuration()):
                    i = 1
                    while i <= self.eventcount:
                        event = self.epgcache.getNextTimeEntry()
                        if event is not None:
                            contentList.append(self.getEventTuple(event))
                        i += 1

                    if self.primetime == 1:
                        now = localtime(time())
                        dt = datetime(now.tm_year, now.tm_mon, now.tm_mday, 20, 15)
                        if time() > mktime(dt.timetuple()):
                            dt += timedelta(days=1)
                        primeTime = int(mktime(dt.timetuple()))
                        if not self.epgcache.startTimeQuery(eServiceReference(ref.toString()), primeTime):
                            event = self.epgcache.getNextTimeEntry()
                            if event and event.getBeginTime() <= int(mktime(dt.timetuple())):
                                contentList.append(self.getEventTuple(event))
            return contentList

    def getEventTuple(self, event):
        time = '%s - %s' % (strftime('%H:%M', localtime(event.getBeginTime())), strftime('%H:%M', localtime(event.getBeginTime() + event.getDuration())))
        title = event.getEventName()
        duration = '%d min' % (event.getDuration() / 60)
        return (time, title, duration)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC:
            Converter.changed(self, what)