# pylint: skip-file
# flake8: noqa
# fmt: off
from lxml import etree

from odoo import tools

TRANSLATED_ELEMENTS = tools.TRANSLATED_ELEMENTS
TRANSLATED_ATTRS = tools.TRANSLATED_ATTRS
SKIPPED_ELEMENT_TYPES = tools.SKIPPED_ELEMENT_TYPES
SKIPPED_ELEMENTS = tools.SKIPPED_ELEMENTS

avoid_pattern = tools.avoid_pattern
parse_html = tools.parse_html


def _check_a_tag(node):
    if node.tag == 'a':
        node.set('href-origin', node.attrib.get('href', ''))
        return True
    return False


# Which attributes must be translated. This is a dict, where the value indicates
# a condition for a node to have the attribute translatable.
TRANSLATED_ATTRS.update({
    'src': lambda node: node.tag in ('img', 'video', 'iframe'),
    'href': lambda node: _check_a_tag(node),
    'data-video-id': lambda node: node.tag == 'div',
})


def translate_xml_node(node, callback, parse, serialize):
    """ Hardcode Odoo to support extended functionality
    ex. module viin_website_multilingual_multimedia: at
    https://viindoo.com/apps/app/15.0/viin_website_multilingual_multimedia
    """
    def nonspace(text):
        """ Return whether ``text`` is a string with non-space characters. """
        return bool(text) and not text.isspace()

    def translatable(node):
        """ Return whether the given node can be translated as a whole. """
        return (
            node.tag in TRANSLATED_ELEMENTS
            and not any(key.startswith("t-") for key in node.attrib)
            and all(translatable(child) for child in node)
        )

    def hastext(node, pos=0):
        """ Return whether the given node contains some text to translate at the
            given child node position.  The text may be before the child node,
            inside it, or after it.
        """
        return (
            # there is some text before node[pos]
            nonspace(node[pos-1].tail if pos else node.text)
            or (
                pos < len(node)
                and translatable(node[pos])
                and (
                    any(  # attribute to translate
                        val and key in TRANSLATED_ATTRS and TRANSLATED_ATTRS[key](node[pos])
                        for key, val in node[pos].attrib.items()
                    )
                    # node[pos] contains some text to translate
                    or hastext(node[pos])
                    # node[pos] has no text, but there is some text after it
                    or hastext(node, pos + 1)
                )
            )
        )

    def process(node):
        """ Translate the given node. """
        if (
            isinstance(node, SKIPPED_ELEMENT_TYPES)
            or node.tag in SKIPPED_ELEMENTS
            or node.get('t-translation', "").strip() == "off"
            or node.tag == 'attribute' and node.get('name') not in TRANSLATED_ATTRS
            or node.getparent() is None and avoid_pattern.match(node.text or "")
        ):
            return

        pos = 0
        while True:
            # check for some text to translate at the given position
            if hastext(node, pos):
                # move all translatable children nodes from the given position
                # into a <div> element
                div = etree.Element('div')
                div.text = (node[pos-1].tail if pos else node.text) or ''
                while pos < len(node) and translatable(node[pos]):
                    div.append(node[pos])

                # translate the content of the <div> element as a whole
                content = serialize(div)[5:-6]
                original = content.strip()
                translated = callback(original)
                if translated:
                    result = content.replace(original, translated)
                    # <div/> is used to auto fix crapy result
                    result_elem = parse_html(f"<div>{result}</div>")
                    # change the tag to <span/> which is one of TRANSLATED_ELEMENTS
                    # so that 'result_elem' can be checked by translatable and hastext
                    result_elem.tag = 'span'
                    #===================================================================
                    # Odoo' code
                    # if translatable(result_elem) and hastext(result_elem):
                    #===================================================================
                    # Override code: start
                    if hastext(result_elem):
                        # Override code: end
                        div = result_elem
                        if pos:
                            node[pos-1].tail = div.text
                        else:
                            node.text = div.text

                # move the content of the <div> element back inside node
                while len(div) > 0:
                    node.insert(pos, div[0])
                    pos += 1

            if pos >= len(node):
                break

            # node[pos] is not translatable as a whole, process it recursively
            process(node[pos])
            pos += 1

        # translate the attributes of the node
        for key, val in node.attrib.items():
            if nonspace(val) and key in TRANSLATED_ATTRS and TRANSLATED_ATTRS[key](node):
                node.set(key, callback(val.strip()) or val)

    process(node)

    return node

translate_xml_node._original_method = tools.translate_xml_node
tools.translate_xml_node = translate_xml_node
tools.translate.translate_xml_node = translate_xml_node
# fmt: on
