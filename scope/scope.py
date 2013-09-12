#
# scope.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

"""Library for code templates serialization."""

import itertools

class SerializerOptions:
	"""Provides additional options for the serialization."""

	DEFAULT_INDENTATION_CHARACTER = ' '
	DEFAULT_INDENTATION_FACTOR = 4

	def __init__(self):
		self._indentation_character = SerializerOptions.DEFAULT_INDENTATION_CHARACTER
		self._indentation_factor = SerializerOptions.DEFAULT_INDENTATION_FACTOR

	@property
	def indentation_character(self):
		"""Indentation character used for serialization."""
		return self._indentation_character

	@indentation_character.setter
	def indentation_character(self, value):
		self._indentation_character = value

	@property
	def indentation_factor(self):
		"""Number of characters to be added for each indent operation."""
		return self._indentation_factor

	@indentation_factor.setter
	def indentation_factor(self, value):
		self._indentation_factor = value

class Scope:
	"""Offer utilities to work with scope-based code templates."""

	def serialize(self, template, options = SerializerOptions()):
		"""Serialize the provided template according to the language specifications."""
		context = SerializerContext(options)
		template.serialize(context)
		return context.output

	def flatten(self, template):
		"""Creates a 'flat' version of the template. It process special s to create a simple structure for the template."""
		return _flatten(template)

class SerializerContext:
	"""Context object for the output generator."""

	def __init__(self, options):
		self._output = ''
		self._indentation = 0
		self._options = options

	def write(self, str):
		"""Print provided string to the output."""
		self._output += self._options.indentation_character * self._indentation + str + '\n'

	def new_line(self):
		"""Add a new blank line."""
		self._output += '\n'

	def indent(self):
		"""Increase line indentation."""
		self._indentation += self._options.indentation_factor

	def unindent(self):
		"""Decrease line indentation."""
		self._indentation -= self._options.indentation_factor

	def serialize(self, object):
		"""Serialize object and print it to the output."""
		if isinstance(object, str):
			self.write(object)
		else:
			object.serialize(self)

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

class TagBase:
	"""Base class for scope-based template tags."""

	def __init__(self):
		self._children = []

	def __repr__(self):
		return '{0} {1}'.format(self.__class__.__name__, self.__dict__)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	def set_arguments(self):
		"""Method called for defining arguments for the object. Should be implemented by subclasses."""
		pass

	def set_children(self, children):
		"""Set the children of the object."""
		self.children = children
		return self

	def serialize(self, context):
		"""Method called for serializing object. Should be implemented by subclasses."""
		pass

	@property
	def children(self):
		"""List of elements assigned to the tag."""
		return self._children

	@children.setter
	def children(self, children):
		self._children = children
		return self

class Tag:
	"""Handler for tag implementations."""

	def __init__(self, class_):
		self._class = class_

	def __call__(self, * args, ** kwargs):
		return _TagImpl(self._class)(* args, ** kwargs)

	def __getitem__(self, children):
		return _TagImpl(self._class)[children]

	def _flatten(self):
		return _flatten(_TagImpl(self._class))

	def _list(self):
		return _list(_TagImpl(self._class))

class IndentTag(TagBase):
	def serialize(self, context):
		context.indent()
		for child in self.children:
			context.serialize(child)
		context.unindent()

class NewLineTag(TagBase):
	def serialize(self, context):
		context.new_line()

#
# Implementation-detail
#

class _TagImpl:
	def __init__(self, class_):
		self._element = class_()
		self._children = []

	def __call__(self, * args, ** kwargs):
		self._element.set_arguments(* args, ** kwargs)
		return self

	def __getitem__(self, children):
		if isinstance(children, tuple):
			self._children = list(children)
		else:
			self._children = [children]
		return self

	def serialize(self, context):
		return _flatten(self).serialize(context)

	def _list(self):
		return [self]

	def _flatten(self):
		source = itertools.chain(* list(_list(t) for t in self._children))
		items = [_flatten(e) for e in source]
		if len(items) > 0:
			self._element.children = items
		return self._element

class _ForEachTag:
	def __init__(self, enumerable, function):
		self._enumerable = enumerable
		self._function = function

	def _list(self):
		return itertools.chain(* list(_list(self._function(e)) for e in self._enumerable))

class _SpanTagImpl:
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

class _SpanTag:
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

#
# Helper tags
#

def for_each(elements, function):
	"""Allows to generate a tag for each items in an enumarable."""
	return _ForEachTag(elements, function)

"""Indent elements in the block."""
indent = Tag(IndentTag)

"""Group elements. These will be appended to the parent."""
span = _SpanTag()

"""Print a new line. It doesn't print indentation."""
new_line = Tag(NewLineTag)
