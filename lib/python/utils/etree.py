#
# A module exporting lxml.etree (high performance) if it exists or xml.etree.ElementTree (Python built-in) otherwise.
#

try:
    from lxml.etree import *

    def createNSElement(namespace, name, nsmap=None):
        return Element('{%s}%s' % (namespace, name), nsmap=nsmap)

    def register_namespace(prefix, uri):
        pass

    def to_pretty_string(element):
        return tostring(element, pretty_print=True)

except ImportError:
    from xml.etree.ElementTree import *
    import xml.etree.ElementTree as _etree

    def createNSElement(namespace, name, nsmap=None):
        return Element('{%s}%s' % (namespace, name))

    try:
        register_namespace = _etree.register_namespace
    except AttributeError:
        def register_namespace(prefix, uri):
            _etree._namespace_map[uri] = prefix #pylint: disable=W0212

    def to_pretty_string(element):
        from xml.dom import minidom
        return minidom.parseString(tostring(element)).toprettyxml()

