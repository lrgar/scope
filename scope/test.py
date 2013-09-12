#
# test.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See accompanying file LICENSE)
#

import unittest
import scope

class MockTag(scope.TagBase):
	def __init__(self):
		super().__init__()
		self._name = ''

	def set_arguments(self, name = ''):
		self._name = name
		return self

	def serialize(self, context):
		context.write('{0}'.format(self._name))
		context.indent()
		for child in self.children:
			context.serialize(child)
		context.unindent()

	@property
	def name(self):
		return self._name

mock_tag = scope.Tag(MockTag)

class TestTemplateSerializer(unittest.TestCase):
	def test_tag_handler_1(self):
		template = mock_tag(name = 'element')

		expected = MockTag().set_arguments(name = 'element')

		self.assertEqual(scope.Scope().flatten(template), expected)

	def test_tag_handler_2(self):
		template = mock_tag(name = 'parent') [
			mock_tag(name = 'child-1'),
			mock_tag(name = 'child-2')
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = [
			MockTag().set_arguments(name = 'child-1'),
			MockTag().set_arguments(name = 'child-2')
		]

		self.assertEqual(scope.Scope().flatten(template), expected)

	def test_tag_handler_3(self):
		template = mock_tag [ mock_tag, mock_tag ]
		expected = MockTag()
		expected.children = [
			MockTag(),
			MockTag()
		]

		self.assertEqual(scope.Scope().flatten(template), expected)

	def test_string_tag_1(self):
		template = mock_tag [ 'abc', mock_tag ]

		expected = MockTag()
		expected.children = [ 'abc', MockTag() ]

		self.assertEqual(scope.Scope().flatten(template), expected)

	def test_tag_for_each_1(self):
		template = mock_tag(name = 'parent') [
			scope.for_each(range(1, 4),
				function = lambda n: mock_tag(name = 'child-{0}'.format(n))
			)
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = [
			MockTag().set_arguments(name = 'child-1'),
			MockTag().set_arguments(name = 'child-2'),
			MockTag().set_arguments(name = 'child-3')
		]

		self.assertEqual(scope.Scope().flatten(template), expected)

	def test_tag_for_each_2(self):
		template = mock_tag(name = 'parent') [
			scope.for_each(range(0, 2),
				function = lambda n: scope.for_each(range(0, 3),
					function = lambda m: mock_tag(name = 'child-{0}'.format(n * 3 + m + 1))
				)
			)
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = [
			MockTag().set_arguments(name = 'child-1'),
			MockTag().set_arguments(name = 'child-2'),
			MockTag().set_arguments(name = 'child-3'),
			MockTag().set_arguments(name = 'child-4'),
			MockTag().set_arguments(name = 'child-5'),
			MockTag().set_arguments(name = 'child-6')
		]

		self.assertEqual(scope.Scope().flatten(template), expected)
		
	def test_tag_for_each_3(self):
		template = mock_tag(name = 'parent') [
			scope.for_each([], function = lambda n: mock_tag)
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = []

		self.assertEqual(scope.Scope().flatten(template), expected)

	def test_tag_span_1(self):
		template = mock_tag(name = 'parent') [
			scope.span [
				mock_tag(name = 'a'),
				mock_tag(name = 'b')
			]
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = [
			MockTag().set_arguments(name = 'a'),
			MockTag().set_arguments(name = 'b')
		]

		self.assertEqual(scope.Scope().flatten(template), expected)
		
	def test_tag_span_2(self):
		template = mock_tag(name = 'parent') [
			scope.span [
				mock_tag(name = 'a'),
				mock_tag(name = 'b')
			],
			scope.span [
				mock_tag(name = 'c'),
				mock_tag(name = 'd')
			]
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = [
			MockTag().set_arguments(name = 'a'),
			MockTag().set_arguments(name = 'b'),
			MockTag().set_arguments(name = 'c'),
			MockTag().set_arguments(name = 'd')
		]

		self.assertEqual(scope.Scope().flatten(template), expected)
	
	def test_tag_span_3(self):
		template = mock_tag(name = 'parent') [
			scope.span [
				mock_tag(name = 'a'),
				scope.span [
					mock_tag(name = 'b'),
					mock_tag(name = 'c')
				],
				mock_tag(name = 'd')
			],
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = [
			MockTag().set_arguments(name = 'a'),
			MockTag().set_arguments(name = 'b'),
			MockTag().set_arguments(name = 'c'),
			MockTag().set_arguments(name = 'd')
		]

		self.assertEqual(scope.Scope().flatten(template), expected)

	def test_tag_span_4(self):
		template = mock_tag(name = 'parent') [
			scope.for_each(range(0, 2),
				function = lambda n: scope.span [
					mock_tag(name = 'a'),
					mock_tag(name = 'b')
				]
			)
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = [
			MockTag().set_arguments(name = 'a'),
			MockTag().set_arguments(name = 'b'),
			MockTag().set_arguments(name = 'a'),
			MockTag().set_arguments(name = 'b')
		]

		self.assertEqual(scope.Scope().flatten(template), expected)

	def test_tag_span_5(self):
		template = mock_tag(name = 'parent') [
			scope.span,
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = []

		self.assertEqual(scope.Scope().flatten(template), expected)
		
	def test_tag_span_6(self):
		template = mock_tag(name = 'parent') [
			scope.span [
				scope.span
			]
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = []

		self.assertEqual(scope.Scope().flatten(template), expected)

	def test_tag_indent_3(self):
		template = mock_tag(name = 'parent') [
			scope.span [
				mock_tag(name = 'a'),
				scope.indent [
					mock_tag(name = 'b'),
					mock_tag(name = 'c')
				],
				mock_tag(name = 'd')
			],
		]
										  
		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = [
			MockTag().set_arguments(name = 'a'),
			scope.IndentTag().set_children([
				MockTag().set_arguments(name = 'b'),
				MockTag().set_arguments(name = 'c')
			]),
			MockTag().set_arguments(name = 'd')
		]

		self.assertEqual(scope.Scope().flatten(template), expected)

	def test_serialization_1(self):
		template = mock_tag(name = 'element')

		expected = 'element\n'

		self.assertEqual(scope.Scope().serialize(template), expected)

	def test_serialization_2(self):
		template = mock_tag(name = 'parent') [
			mock_tag(name = 'child-1'),
			mock_tag(name = 'child-2')
		]

		expected = 'parent\n    child-1\n    child-2\n'

		self.assertEqual(scope.Scope().serialize(template), expected)
		
	def test_serialization_3(self):
		template = mock_tag(name = 'element')

		expected = 'element\n'

		self.assertEqual(scope.Scope().serialize(scope.Scope().flatten(template)), expected)
		
	def test_serialization_4(self):
		template = mock_tag(name = 'parent') [
			mock_tag(name = 'child-1'),
			scope.indent [
				mock_tag(name = 'child-2')
			]
		]

		expected = 'parent\n    child-1\n        child-2\n'

		self.assertEqual(scope.Scope().serialize(template), expected)
		
	def test_serialization_5(self):
		template = mock_tag(name = 'parent') [
			mock_tag(name = 'child-1'),
			'',
			scope.indent [
				'str:child-2'
			]
		]

		expected = 'parent\n    child-1\n    \n        str:child-2\n'

		self.assertEqual(scope.Scope().serialize(template), expected)
		
	def test_serialization_6(self):
		template = mock_tag(name = 'parent') [
			mock_tag(name = 'child-1'),
			scope.new_line,
			scope.indent [
				'str:child-2'
			]
		]

		expected = 'parent\n    child-1\n\n        str:child-2\n'

		self.assertEqual(scope.Scope().serialize(template), expected)
		
	def test_serialization_7(self):
		options = scope.SerializationOptions()
		options.indentation_character = '\t'
		options.indentation_factor = 1

		template = mock_tag(name = 'parent') [
			mock_tag(name = 'child-1'),
			scope.new_line,
			scope.indent [
				'str:child-2'
			]
		]

		expected = 'parent\n\tchild-1\n\n\t\tstr:child-2\n'

		self.assertEqual(scope.Scope().serialize(template, options), expected)

if __name__ == '__main__':
	unittest.main()
