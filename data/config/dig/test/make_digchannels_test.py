#!/bin/env python
# @(#) $Header$

"""
Create digchannels_test.xml by substituting some values in digchannels.xml.
"""

from xml.dom.minidom import parse, NamedNodeMap


def convert(input="../../../../etc/dig/digchannels.xml", output="digchannels_test.xml"):
    """ Update digchannels.xml to use MQ for input and output. """
    dom = parse(input)

    newqueues = set(())
    for channel in dom.getElementsByTagName("channel"):
        # Add logCategories
        channel.attributes['logCategories'] = "+D"

        for reader in channel.getElementsByTagName("reader"):
            if reader.getAttribute("class") == "carmensystems.dig.scheduler.job.JobReader":
                queuename = channel.attributes["name"].value.upper() + "_TEST"
                # Change JobReader to MQReader
                for a in reader.attributes.keys():
                    reader.removeAttribute(a)
                reader.attributes["class"] = "carmensystems.dig.readers.jmq.MQReader"
                reader.attributes["host"] = "%(site/mq/server)"
                reader.attributes["port"] = "%(site/mq/port)"
                reader.attributes["manager"] = "%(site/mq/manager)"
                reader.attributes["channel"] = "%(site/mq/channel)"
                reader.attributes["altUser"] = "%(site/mq/altuser)"
                reader.attributes["queue"] = queuename
                reader.attributes["numToRead"] = "-1"
                newqueues.add(queuename)
                
        for messagehandlers in channel.getElementsByTagName("messagehandlers"):
            for mh in messagehandlers.getElementsByTagName("messagehandler"):
                # Remove any existing AddressInjector
                if mh.getAttribute("class") == "dig.xhandlers.AddressInjector":
                    messagehandlers.removeChild(mh)

                # Redirect all output to MQ
                # Update TransportDispatcher to use MQ specific info
                elif mh.getAttribute("class") == "carmensystems.dig.messagehandlers.transport.TransportDispatcher":
                    for a in mh.attributes.keys():
                        # Remove all old attributes except for the attribute "class"
                        if a != "class":
                            mh.removeAttribute(a)
                    mh.setAttribute('mqreply_host', "%(site/mq/server)")
                    mh.setAttribute('mqreply_port', "%(site/mq/port)")
                    mh.setAttribute('mqreply_channel',"%(site/mq/channel)")
                    mh.setAttribute('mqreply_altUser',"%(site/mq/altuser)")
                    # Insert AddressInjector to send all output to mqreply
                    addrinj = dom.createElement('messagehandler')
                    addrinj.setAttribute('ALL_dests', "REPLY")
                    addrinj.setAttribute('REPLY_protocol', "mqreply")
                    addrinj.setAttribute('class','dig.xhandlers.AddressInjector')
                    messagehandlers.insertBefore(addrinj,mh)

                # Change ReportTranslator to ReportRequestBuilder
                elif mh.getAttribute("class") == "carmensystems.dig.scheduler.reports.ReportTranslator":
                    for a in mh.attributes.keys():
                        mh.removeAttribute(a)
                    mh.setAttribute('class', "dig.xhandlers.ReportRequestBuilder")
                    mh.setAttribute('configFile',"$(CARMUSR)/data/config/dig/test/reports.publish.test")
                    mh.setAttribute('paramSeparator',",")
                    mh.setAttribute('delta', "True")
                    mh.setAttribute('overrideServerArgs', "True")

                # Change ReportHandler to ReportRequestHandler
                elif mh.getAttribute("class") == "carmensystems.dig.messagehandlers.reports.ReportHandler":
                    mh.setAttribute('class', "carmensystems.dig.messagehandlers.reports.ReportRequestHandler")

                # Change StaticMQWriter to ReplyMQWriter
                elif mh.getAttribute("class") == "carmensystems.dig.messagehandlers.jmq.StaticMQWriter":
                    for a in mh.attributes.keys():
                        mh.removeAttribute(a)
                    mh.setAttribute('class', "carmensystems.dig.messagehandlers.jmq.ReplyMQWriter")
                    mh.setAttribute('host', "%(site/mq/server)")
                    mh.setAttribute('port', "%(site/mq/port)")
                    mh.setAttribute('channel',"%(site/mq/channel)")
                    mh.setAttribute('altUser',"%(site/mq/altuser)")

                # Remove Trigger form "baggage" and "loadsheet" channels
                elif mh.getAttribute("class") == "dig.triggers.FlightDepartureTrigger":
                    if channel.getAttribute("name") in ("baggage","loadsheet"):
                        for a in mh.attributes.keys():
                            mh.removeAttribute(a)
                        mh.setAttribute('class', "dig.xhandlers.DebugLogger")
                    elif channel.getAttribute("name").startswith("manifest"):
                        for a in mh.attributes.keys():
                            mh.removeAttribute(a)
                        mh.setAttribute('class', "dig.xhandlers.ReportRequestBuilder")
                        mh.setAttribute('configFile',"$(CARMUSR)/data/config/dig/test/reports.publish.test")
                        mh.setAttribute('paramSeparator',",")
                        mh.setAttribute('delta', "True")
                

    f = open(output, "w")
    print >>f, dom.toxml()
    f.close()

    print "These queues will have to exist:\n" + '\n'.join(["\t%s" % q for q in sorted(newqueues)])
    print "Queue definition file testqueues.mq has been created."
    
    f = open("testqueues.mq", "w")
    for q in newqueues:
        print >>f, "DEF QL(%s) REPLACE" % q
    f.close()


if __name__ == '__main__':
    convert()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
