﻿#
# scope.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See file LICENSE)
#

"""Library for code template serialization."""

import itertools


class SerializerOptions(object):
    """Provides additional options for the serialization."""

    DEFAULT_INDENTATION_CHARACTER = ' '
    DEFAULT_INDENTATION_FACTOR = 4

    def __init__(self):
        self._indentation_character = \
            SerializerOptions.DEFAULT_INDENTATION_CHARACTER
        self._indentation_factor = \
            SerializerOptions.DEFAULT_INDENTATION_FACTOR

    @property
    def indentation_character(self):
        """Indentation character used for serialization."""
        return self._indentation_character

    @indentation_character.setter
    def indentation_character(self, value):
        """Set character used for indentation"""
        self._indentation_character = value

    @property
    def indentation_factor(self):
        """Number of characters to be added for each indent operation."""
        return self._indentation_factor

    @indentation_factor.setter
    def indentation_factor(self, value):
        """Set the factor of characters used for indentation"""
        self._indentation_factor = value


class SerializerContext(object):
    """Context object for the output generator."""

    def __init__(self, options):
        self._output = ''
        self._indentation = 0
        self._options = options

    def write(self, string):
        """Print provided string to the output."""
        self._output += self._options.indentation_character * \
            self._indentation + string + '\n'

    def new_line(self):
        """Add a new blank line."""
        self._output += '\n'

    def indent(self):
        """Increase line indentation."""
        self._indentation += self._options.indentation_factor

    def unindent(self):
        """Decrease line indentation."""
        self._indentation -= self._options.indentation_factor

    def serialize(self, tag):
        """Serialize tag and print it to the output."""
        if isinstance(tag, str):
            self.write(tag)
        else:
            tag.serialize(self)

    @property
    def indentation(self):
        """Current indentation, in units for the serializer."""
        return self._indentation

    @property
    def output(self):
        """Output of the serializer."""
        return self._output

    @property
    def options(self):
        """Options for the serializer."""
        return self._options


class TagBase(object):
    """Base class for scope-based template tags."""

    def __init__(self):
        self._children = []

    def __repr__(self):
        return '{0} {1}'.format(self.__class__.__name__, self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def set_children(self, children):
        """Set the children of the object."""
        self.children = children
        return self

    def serialize(self, context):
        """Method called for serializing object. Should be implemented by
        subclasses."""
        pass

    @property
    def children(self):
        """List of elements assigned to the tag."""
        return self._children

    @children.setter
    def children(self, children):
        """Set the childrend of the object."""
        self._children = children
        return self


class Tag(object):
    """Handler for tag implementations."""

    def __init__(self, class_):
        self._class = class_

    def __call__(self, * args, ** kwargs):
        return _TagImpl(self._class).set_arguments(* args, ** kwargs)

    def __getitem__(self, children):
        return _TagImpl(self._class).set_arguments()[children]

    def _flatten(self):
        """Creates a 'flat' representation of itself."""
        return _flatten(_TagImpl(self._class).set_arguments())

    def _list(self):
        """Returns a list of items 'flat' representation of itself."""
        return _list(_TagImpl(self._class).set_arguments())


class IndentTag(TagBase):
    """Represents an indent tag, the children will be printed with increased
    indentation."""

    def serialize(self, context):
        context.indent()
        for child in self.children:
            context.serialize(child)
        context.unindent()


class NewLineTag(TagBase):
    """Represents a blank line tag."""

    def serialize(self, context):
        context.new_line()


class _TagImpl(object):
    """Proxy object to manage a tag before it becomes flattened."""

    def __init__(self, class_):
        self._class = class_
        self._children = []
        self._element = None

    def set_arguments(self, * args, ** kwargs):
        self._element = self._class(* args, ** kwargs)
        return self

    def __getitem__(self, children):
        if isinstance(children, tuple):
            self._children = list(children)
        else:
            self._children = [children]
        return self

    def serialize(self, context):
        """Proxy object to manage a tag before it becomes flattened."""
        return _flatten(self).serialize(context)

    def _list(self):
        return [self]

    def _flatten(self):
        source = itertools.chain(* list(_list(t) for t in self._children))
        items = [_flatten(e) for e in source]
        if len(items) > 0:
            self._element.children = items
        return self._element


class _ForEachTag(object):
    def __init__(self, enumerable, function):
        self._enumerable = enumerable
        self._function = function

    def _list(self):
        return itertools.chain(
            * list(_list(self._function(e)) for e in self._enumerable))


class _SpanTagImpl(object):
    def __init__(self):
        self._children = []

    def __getitem__(self, children):
        if isinstance(children, tuple):
            self._children = list(children)
        else:
            self._children = [children]
        return self

    def _list(self):
        return itertools.chain(* list(_list(e) for e in self._children))


class _SpanTag(object):
    def __init__(self):
        self._children = []

    def __getitem__(self, children):
        return _SpanTagImpl()[children]

    def _list(self):
        return _SpanTagImpl()._list()


def _flatten(value):
    if isinstance(value, str):
        return value
    else:
        return value._flatten()


def _list(value):
    if isinstance(value, str):
        return [value]
    else:
        return value._list()


def for_each(elements, function):
    """Allows to generate a tag for each items in an enumarable."""
    return _ForEachTag(elements, function)

# Indent elements in the block.
indent = Tag(IndentTag)     # pylint: disable-msg=C0103

# Group elements. These will be appended to the parent.
span = _SpanTag()           # pylint: disable-msg=C0103

# Print a new line. It doesn't print indentation.
new_line = Tag(NewLineTag)  # pylint: disable-msg=C0103


def serialize(template, options=SerializerOptions()):
    """Serialize the provided template according to the language
    specifications."""
    context = SerializerContext(options)
    template.serialize(context)
    return context.output


def flatten(template):
    """Creates a 'flat' version of the template. It process special s to
    create a simple structure for the template."""
    return _flatten(template)
