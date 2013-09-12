#
# cpp.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

import scope

class SingletonObject:
	def __init__(self, name):
		self._name = name

	def __repr__(self):
		return '<{0}>'.format(self._name)

PUBLIC = SingletonObject('public')
PRIVATE = SingletonObject('private')
PROTECTED = SingletonObject('protected')
DEFAULT = SingletonObject('default')

class CppFile(scope.TagBase):
	def __init__(self):
		super().__init__()
		
	def set_arguments(self):
		return self
	
	def serialize(self, context):
		for child in self.children:
			context.serialize(child)

class CppNamespace(scope.TagBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, name):
		self._name = name
		return self

	def serialize(self, context):
		context.write('namespace {0} {{'.format(self._name))
		context.indent()
		for child in self.children:
			context.serialize(child)
		context.unindent()
		context.write('}} // namespace {0}'.format(self._name))

	@property
	def name(self):
		return self._name

class CppClass(scope.TagBase):
	def __init__(self, unit_name = 'class'):
		super().__init__()
		self._unit_name = unit_name

	def set_arguments(self, name, superclasses = [], visibility = DEFAULT):
		self._name = name
		self._visibility = visibility
		self._superclasses = superclasses
		return self

	def serialize(self, context):
		temp = '{0} {1}'.format(self._unit_name, self._name)
		if len(self._superclasses) > 0:
			format = lambda v, n: '{0} {1}'.format(_from_visibility_to_string(v), n)
			temp += ' : ' + ', '.join([format(v, n) for v, n in self._superclasses])
		temp += ' {'

		context.write(temp)

		private_children = _filter_by_visibility(self.children, [PRIVATE, DEFAULT])
		if len(private_children) > 0:
			_indent_and_print_elements(context, private_children)

		public_children = _filter_by_visibility(self.children, [PUBLIC])
		if len(public_children) > 0:
			context.write('public:')
			_indent_and_print_elements(context, public_children)

		protected_children = _filter_by_visibility(self.children, [PROTECTED])
		if len(protected_children) > 0:
			context.write('protected:')
			_indent_and_print_elements(context, protected_children)

		context.write('}}; // class {0}'.format(self._name))

	@property
	def name(self):
		return self._name

	@property
	def visibility(self):
		return self._visibility

	@property
	def superclasses(self):
		return self._superclasses

def _from_visibility_to_string(visibility):
	if visibility is PUBLIC:
		return 'public'
	elif visibility is PRIVATE:
		return 'private'
	elif visibility is PROTECTED:
		return 'protected'
	else:
		raise ValueError('Invalid value for visibility.')

def _filter_by_visibility(children, filter):
	return [child for child in children if child.visibility in filter]

def _indent_and_print_elements(context, elements):
	context.indent()
	for child in elements:
		context.serialize(child)
	context.unindent()

tfile = scope.Tag(CppFile)
tnamespace = scope.Tag(CppNamespace)
tclass = scope.Tag(CppClass)
