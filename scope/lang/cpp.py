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

	def set_arguments(self, name = None):
		self._name = name
		return self

	def serialize(self, context):
		if self._name is None:
			context.write('namespace {')
		else:
			context.write('namespace {0} {{'.format(self._name))

		context.indent()
		for child in self.children:
			context.serialize(child)
		context.unindent()

		if self._name is None:
			context.write('} // namespace')
		else:
			context.write('}} // namespace {0}'.format(self._name))

	@property
	def name(self):
		return self._name

class CppClass(scope.TagBase):
	def __init__(self, unit_name = 'class', default_visibility = PRIVATE):
		super().__init__()
		self._unit_name = unit_name
		self._default_visibility = default_visibility

	def set_arguments(self, name, *, superclasses = [], visibility = DEFAULT):
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

		if self._default_visibility == PRIVATE:
			self._print_children(context, PRIVATE)
			self._print_children(context, PUBLIC, 'public:')
		elif self._default_visibility == PUBLIC:
			self._print_children(context, PUBLIC)
			self._print_children(context, PRIVATE, 'private:')

		self._print_children(context, PROTECTED, 'protected:')

		context.write('}}; // {0} {1}'.format(self._unit_name, self._name))

	def _print_children(self, context, visibility, section_name = None):
		selected = _filter_by_visibility(self.children, visibility, self._default_visibility)
		if len(selected) > 0:
			if section_name is not None:
				context.write(section_name)
			_indent_and_print_elements(context, selected)

	@property
	def name(self):
		return self._name

	@property
	def visibility(self):
		return self._visibility

	@property
	def superclasses(self):
		return self._superclasses

class CppStruct(CppClass):
	def __init__(self):
		super().__init__('struct', PUBLIC)

class CppMethodBase(scope.TagBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, return_type, name, arguments = [], *, visibility = DEFAULT, implemented = True, virtual = False, const = False):
		self._return_type = return_type
		self._name = name
		self._visibility = visibility
		self._virtual = virtual
		self._arguments = arguments
		self._implemented = implemented
		self._const = const
		return self

	def serialize(self, context):
		temp = ''
		if self._virtual: temp += 'virtual '

		args = ', '.join(self._arguments)
		if self._return_type is not None: temp += self._return_type + ' '
		temp += '{1}({2})'.format(self._return_type, self._name, args)

		if self._const: temp += ' const'

		if len(self.children) > 0:
			context.write(temp + ' {')
			_indent_and_print_elements(context, self.children)
			context.write('}')
		elif self._implemented:
			context.write(temp + ' {}')
		else:
			context.write(temp + ';')

	@property
	def return_type(self):
		return self._return_type

	@property
	def name(self):
		return self._name

	@property
	def arguments(self):
		return self._arguments

	@property
	def virtual(self):
		return self._virtual

	@property
	def const(self):
		return self._const

	@property
	def implemented(self):
		return self._implemented

	@property
	def visibility(self):
		return self._visibility

class CppMethod(CppMethodBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, return_type, name, arguments = [], *, visibility = DEFAULT, implemented = True, virtual = False, const = False):
		return super().set_arguments(
			return_type, name, arguments,
			visibility = visibility,
			implemented = implemented,
			virtual = virtual,
			const = const
		)
	
class CppConstructor(CppMethodBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, name, arguments = [], *, visibility = DEFAULT, implemented = True):
		return super().set_arguments(
			None, name, arguments,
			visibility = visibility,
			implemented = implemented
		)

class CppDestructor(CppMethodBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, name, *, visibility = DEFAULT, implemented = True, virtual = False):
		return super().set_arguments(
			None, name, [],
			visibility = visibility,
			implemented = implemented,
			virtual = virtual
		)

class CppAttribute(scope.TagBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, type, name, *, visibility = DEFAULT, static = False, const = False, default_value = None):
		self._type = type
		self._name = name
		self._visibility = visibility
		self._static = static
		self._const = const
		self._default_value = default_value
		return self

	def serialize(self, context):
		line = ''
		if self._static: line += 'static '
		if self._const: line += 'const '
		line += '{0} {1}'.format(self._type, self._name)
		if self._default_value is not None:
			line += ' = {0}'.format(self._default_value)
		line += ';'

		context.write(line)

	@property
	def type(self):
		return self._type

	@property
	def name(self):
		return self._name

	@property
	def visibility(self):
		return self._visibility

	@property
	def static(self):
		return self._static

	@property
	def const(self):
		return self._const

	@property
	def default_value(self):
		return self._default_value

class CppEnum(scope.TagBase):
	def __init__(self):
		super().__init__()

	def set_arguments(self, name, values, *, visibility = PUBLIC):
		self._name = name
		self._values = values
		self._visibility = visibility
		return self

	def serialize(self, context):
		if len(self._values) > 0:
			context.write('enum {0} {{'.format(self._name))
			context.indent()
			for value in self._values[:-1]: context.write('{0},'.format(value))
			context.write('{0}'.format(self._values[-1]))
			context.unindent()
			context.write('};')
		else:
			context.write('enum {0} {{}};'.format(self._name))

	@property
	def name(self):
		return self._name

	@property
	def values(self):
		return self._values

	@property
	def visibility(self):
		return self._visibility

def _from_visibility_to_string(visibility):
	if visibility is PUBLIC:
		return 'public'
	elif visibility is PRIVATE:
		return 'private'
	elif visibility is PROTECTED:
		return 'protected'
	else:
		raise ValueError('Invalid value for visibility.')

def _filter_by_visibility(children, visibility, default_visibility):
	if default_visibility == visibility:
		return [child for child in children if child.visibility in [visibility, DEFAULT]]
	else:
		return [child for child in children if child.visibility == visibility]

def _indent_and_print_elements(context, elements):
	context.indent()
	for child in elements:
		context.serialize(child)
	context.unindent()

tfile = scope.Tag(CppFile)
tnamespace = scope.Tag(CppNamespace)
tclass = scope.Tag(CppClass)
tstruct = scope.Tag(CppStruct)
tmethod = scope.Tag(CppMethod)
tctor = scope.Tag(CppConstructor)
tdtor = scope.Tag(CppDestructor)
tattribute = scope.Tag(CppAttribute)
tenum = scope.Tag(CppEnum)
