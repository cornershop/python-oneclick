#!/usr/bin/python
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

"""Simple XML manipulation"""


from __future__ import unicode_literals
import sys
if sys.version > '3':
    basestring = str
    unicode = str

import re
import time
import xml.dom.minidom


class SimpleXMLElement(object):
    """Simple XML manipulation (simil PHP)"""

    def __init__(self, text=None, elements=None, document=None,
                 namespace=None, prefix=None, namespaces_map={}, jetty=False):
        """
        :param namespaces_map: How to map our namespace prefix to that given by the client;
          {prefix: received_prefix}
        """
        self.__namespaces_map = namespaces_map
        _rx = "|".join(namespaces_map.keys())  # {'external': 'ext', 'model': 'mod'} -> 'external|model'
        self.__ns_rx = re.compile(r"^(%s):.*$" % _rx)  # And now we build an expression ^(external|model):.*$
                                                       # to find prefixes in all xml nodes i.e.: <model:code>1</model:code>
                                                       # and later change that to <mod:code>1</mod:code>
        self.__ns = namespace
        self.__prefix = prefix
        self.__jetty = jetty                           # special list support

        if text is not None:
            try:
                self.__document = xml.dom.minidom.parseString(text)
            except:
                raise
            self.__elements = [self.__document.documentElement]
        else:
            self.__elements = elements
            self.__document = document

    def add_child(self, name, text=None, ns=True):
        """Adding a child tag to a node"""
        if not ns or self.__ns is False:
            element = self.__document.createElement(name)
        else:
            if isinstance(ns, basestring):
                element = self.__document.createElement(name)
                if ns:
                    element.setAttribute("xmlns", ns)
            elif self.__prefix:
                element = self.__document.createElementNS(self.__ns, "%s:%s" % (self.__prefix, name))
            else:
                element = self.__document.createElementNS(self.__ns, name)
        # don't append null tags!
        if text is not None:
            if isinstance(text, xml.dom.minidom.CDATASection):
                element.appendChild(self.__document.createCDATASection(text.data))
            else:
                element.appendChild(self.__document.createTextNode(text))
        self._element.appendChild(element)
        return SimpleXMLElement(
            elements=[element],
            document=self.__document,
            namespace=self.__ns,
            prefix=self.__prefix,
            jetty=self.__jetty,
            namespaces_map=self.__namespaces_map
        )

    def __setattr__(self, tag, text):
        """Add text child tag node (short form)"""
        if tag.startswith("_"):
            object.__setattr__(self, tag, text)
        else:
            self.add_child(tag, text)

    def __delattr__(self, tag):
        """Remove a child tag (non recursive!)"""
        elements = [__element for __element in self._element.childNodes
                    if __element.nodeType == __element.ELEMENT_NODE]
        for element in elements:
            self._element.removeChild(element)

    def add_comment(self, data):
        """Add an xml comment to this child"""
        comment = self.__document.createComment(data)
        self._element.appendChild(comment)

    def as_xml(self, filename=None, pretty=False):
        """Return the XML representation of the document"""
        if not pretty:
            return self.__document.toxml('UTF-8')
        else:
            return self.__document.toprettyxml(encoding='UTF-8')

    if sys.version > '3':
        def __repr__(self):
            """Return the XML representation of this tag"""
            return self._element.toxml()
    else:
        def __repr__(self):
            """Return the XML representation of this tag"""
            # NOTE: do not use self.as_xml('UTF-8') as it returns the whole xml doc
            return self._element.toxml('UTF-8')

    def get_name(self):
        """Return the tag name of this node"""
        return self._element.tagName

    def get_local_name(self):
        """Return the tag local name (prefix:name) of this node"""
        return self._element.localName

    def get_prefix(self):
        """Return the namespace prefix of this node"""
        return self._element.prefix

    def get_namespace_uri(self, ns):
        """Return the namespace uri for a prefix"""
        element = self._element
        while element is not None and element.attributes is not None:
            try:
                return element.attributes['xmlns:%s' % ns].value
            except KeyError:
                element = element.parentNode

    def attributes(self):
        """Return a dict of attributes for this tag"""
        #TODO: use slice syntax [:]?
        return self._element.attributes

    def __getitem__(self, item):
        """Return xml tag attribute value or a slice of attributes (iter)"""
        if isinstance(item, basestring):
            if self._element.hasAttribute(item):
                return self._element.attributes[item].value
        elif isinstance(item, slice):
            # return a list with name:values
            return list(self._element.attributes.items())[item]
        else:
            # return element by index (position)
            element = self.__elements[item]
            return SimpleXMLElement(
                elements=[element],
                document=self.__document,
                namespace=self.__ns,
                prefix=self.__prefix,
                jetty=self.__jetty,
                namespaces_map=self.__namespaces_map
            )

    def add_attribute(self, name, value):
        """Set an attribute value from a string"""
        self._element.setAttribute(name, value)

    def __setitem__(self, item, value):
        """Set an attribute value"""
        if isinstance(item, basestring):
            self.add_attribute(item, value)
        elif isinstance(item, slice):
            # set multiple attributes at once
            for k, v in value.items():
                self.add_attribute(k, v)

    def __delitem__(self, item):
        "Remove an attribute"
        self._element.removeAttribute(item)

    def __call__(self, tag=None, ns=None, children=False, root=False,
                 error=True, ):
        """Search (even in child nodes) and return a child tag by name"""
        try:
            if root:
                # return entire document
                return SimpleXMLElement(
                    elements=[self.__document.documentElement],
                    document=self.__document,
                    namespace=self.__ns,
                    prefix=self.__prefix,
                    jetty=self.__jetty,
                    namespaces_map=self.__namespaces_map
                )
            if tag is None:
                # if no name given, iterate over siblings (same level)
                return self.__iter__()
            if children:
                # future: filter children? by ns?
                return self.children()
            elements = None
            if isinstance(tag, int):
                # return tag by index
                elements = [self.__elements[tag]]
            if ns and not elements:
                for ns_uri in isinstance(ns, (tuple, list)) and ns or (ns, ):
                    elements = self._element.getElementsByTagNameNS(ns_uri, tag)
                    if elements:
                        break
            if self.__ns and not elements:
                elements = self._element.getElementsByTagNameNS(self.__ns, tag)
            if not elements:
                elements = self._element.getElementsByTagName(tag)
            if not elements:
                if error:
                    raise AttributeError("No elements found")
                else:
                    return
            return SimpleXMLElement(
                elements=elements,
                document=self.__document,
                namespace=self.__ns,
                prefix=self.__prefix,
                jetty=self.__jetty,
                namespaces_map=self.__namespaces_map)
        except AttributeError as e:
            raise AttributeError("Tag not found: %s (%s)" % (tag, e))

    def __getattr__(self, tag):
        """Shortcut for __call__"""
        return self.__call__(tag)

    def __iter__(self):
        """Iterate over xml tags at this level"""
        try:
            for __element in self.__elements:
                yield SimpleXMLElement(
                    elements=[__element],
                    document=self.__document,
                    namespace=self.__ns,
                    prefix=self.__prefix,
                    jetty=self.__jetty,
                    namespaces_map=self.__namespaces_map)
        except:
            raise

    def __dir__(self):
        """List xml children tags names"""
        return [node.tagName for node
                in self._element.childNodes
                if node.nodeType != node.TEXT_NODE]

    def children(self):
        """Return xml children tags element"""
        elements = [__element for __element in self._element.childNodes
                    if __element.nodeType == __element.ELEMENT_NODE]
        if not elements:
            return None
            #raise IndexError("Tag %s has no children" % self._element.tagName)
        return SimpleXMLElement(
            elements=elements,
            document=self.__document,
            namespace=self.__ns,
            prefix=self.__prefix,
            jetty=self.__jetty,
            namespaces_map=self.__namespaces_map
        )

    def __len__(self):
        """Return element count"""
        return len(self.__elements)

    def __contains__(self, item):
        """Search for a tag name in this element or child nodes"""
        return self._element.getElementsByTagName(item)

    def __unicode__(self):
        """Returns the unicode text nodes of the current element"""
        rc = ''
        for node in self._element.childNodes:
            if node.nodeType == node.TEXT_NODE or node.nodeType == node.CDATA_SECTION_NODE:
                rc = rc + node.data
        return rc

    if sys.version > '3':
        __str__ = __unicode__
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

    def __int__(self):
        """Returns the integer value of the current element"""
        return int(self.__str__())

    def __float__(self):
        """Returns the float value of the current element"""
        try:
            return float(self.__str__())
        except:
            raise IndexError(self._element.toxml())

    _element = property(lambda self: self.__elements[0])

    def _update_ns(self, name):
        """Replace the defined namespace alias with tohse used by the client."""
        pref = self.__ns_rx.search(name)
        if pref:
            pref = pref.groups()[0]
            try:
                name = name.replace(pref, self.__namespaces_map[pref])
            except KeyError:
                pass
        return name

    def import_node(self, other):
        x = self.__document.importNode(other._element, True)  # deep copy
        self._element.appendChild(x)

    def write_c14n(self, output=None, exclusive=True):
        "Generate the canonical version of the XML node"
        from . import c14n
        xml = c14n.Canonicalize(self._element, output,
                                unsuppressedPrefixes=[] if exclusive else None)
        return xml