#
# template_serializer.py
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

	def test_tag_block_1(self):
		template = mock_tag(name = 'parent') [
			scope.block [
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
		
	def test_tag_block_2(self):
		template = mock_tag(name = 'parent') [
			scope.block [
				mock_tag(name = 'a'),
				mock_tag(name = 'b')
			],
			scope.block [
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
	
	def test_tag_block_3(self):
		template = mock_tag(name = 'parent') [
			scope.block [
				mock_tag(name = 'a'),
				scope.block [
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

	def test_tag_block_4(self):
		template = mock_tag(name = 'parent') [
			scope.for_each(range(0, 2),
				function = lambda n: scope.block [
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

	def test_tag_block_5(self):
		template = mock_tag(name = 'parent') [
			scope.block,
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = []

		self.assertEqual(scope.Scope().flatten(template), expected)
		
	def test_tag_block_6(self):
		template = mock_tag(name = 'parent') [
			scope.block [
				scope.block
			]
		]

		expected = MockTag()
		expected.set_arguments(name = 'parent')
		expected.children = []

		self.assertEqual(scope.Scope().flatten(template), expected)

if __name__ == '__main__':
	unittest.main()
