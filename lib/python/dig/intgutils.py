"""
  Various Integration Utility Functions
"""
from utils.ServiceConfig import ServiceConfig
"""
Complementary services not provided by the config API
"""
class IntgServiceConfig(ServiceConfig):
    def getDIGChannelAttr(self, channel, attr):
        props = self.getProperties("dig/channel/messagehandlers/messagehandler@%s" % attr)
        for (key,value) in props:
            if key.find("dig/%s"%channel) > 0:
                return value
        raise Exception("getDIGChannelAttr: Cannot find attribute '%s' in channel '%s'" %(attr, channel))

    def getRSWorkerFromPortal(self, portalService):
        props = self.getProperties("reportserver/process/portal_service")
        for (key,value) in props:
            if value == portalService:
                k,v = self.getProperty(key.replace('/portal_service','') + '@name')
                return v
        raise Exception("getRSWorkerFromPortal: Cannot find worker for portal %s" % portalService)
