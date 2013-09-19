#
# test.py
#
# Copyright (c) 2013 Luis Garcia.
# This source file is subject to terms of the MIT License. (See file LICENSE)
#

# pylint: disable=C0111

import unittest
import scope
import lang.cpp as cpp


class MockTag(scope.TagBase):
    def __init__(self, name=''):
        super().__init__()
        self._name = name

    def serialize(self, context):
        context.write('{0}'.format(self._name))
        context.indent()
        for child in self.children:
            context.serialize(child)
        context.unindent()

    @property
    def name(self):
        return self._name

mock_tag = scope.Tag(MockTag)  # pylint: disable-msg=C0103


class TestBaseLibrary(unittest.TestCase):  # pylint: disable-msg=R0904
    def test_tag_handler_1(self):
        template = mock_tag(name='element')

        expected = MockTag(name='element')

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_handler_2(self):
        template = mock_tag(name='parent')[
            mock_tag(name='child-1'),
            mock_tag(name='child-2')
        ]

        expected = MockTag(name='parent')
        expected.children = [
            MockTag(name='child-1'),
            MockTag(name='child-2')
        ]

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_handler_3(self):
        template = mock_tag[mock_tag, mock_tag]

        expected = MockTag()
        expected.children = [
            MockTag(),
            MockTag()
        ]

        self.assertEqual(scope.flatten(template), expected)

    def test_string_tag_1(self):
        template = mock_tag['abc', mock_tag]

        expected = MockTag()
        expected.children = ['abc', MockTag()]

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_for_each_1(self):
        template = mock_tag(name='parent')[
            scope.for_each(
                range(1, 4),
                lambda n: mock_tag(name='child-{0}'.format(n))
            )
        ]

        expected = MockTag(name='parent')
        expected.children = [
            MockTag(name='child-1'),
            MockTag(name='child-2'),
            MockTag(name='child-3')
        ]

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_for_each_2(self):
        def gen(i):
            return scope.for_each(
                range(0, 3),
                function=lambda j: mock_tag(
                    name='child-{0}'.format(i * 3 + j + 1)
                )
            )

        template = mock_tag(name='parent')[
            scope.for_each(range(0, 2), function=gen)
        ]

        expected = MockTag(name='parent')
        expected.children = [
            MockTag(name='child-1'),
            MockTag(name='child-2'),
            MockTag(name='child-3'),
            MockTag(name='child-4'),
            MockTag(name='child-5'),
            MockTag(name='child-6')
        ]

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_for_each_3(self):
        template = mock_tag(name='parent')[
            scope.for_each([], function=lambda n: mock_tag)
        ]

        expected = MockTag(name='parent')
        expected.children = []

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_span_1(self):
        template = mock_tag(name='parent')[
            scope.span[
                mock_tag(name='a'),
                mock_tag(name='b')
            ]
        ]

        expected = MockTag(name='parent')
        expected.children = [
            MockTag(name='a'),
            MockTag(name='b')
        ]

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_span_2(self):
        template = mock_tag(name='parent')[
            scope.span[
                mock_tag(name='a'),
                mock_tag(name='b')
            ],
            scope.span[
                mock_tag(name='c'),
                mock_tag(name='d')
            ]
        ]

        expected = MockTag(name='parent')
        expected.children = [
            MockTag(name='a'),
            MockTag(name='b'),
            MockTag(name='c'),
            MockTag(name='d')
        ]

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_span_3(self):
        template = mock_tag(name='parent')[
            scope.span[
                mock_tag(name='a'),
                scope.span[
                    mock_tag(name='b'),
                    mock_tag(name='c')
                ],
                mock_tag(name='d')
            ],
        ]

        expected = MockTag(name='parent')
        expected.children = [
            MockTag(name='a'),
            MockTag(name='b'),
            MockTag(name='c'),
            MockTag(name='d')
        ]

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_span_4(self):
        template = mock_tag(name='parent')[
            scope.for_each(
                range(0, 2),
                lambda n: scope.span[
                    mock_tag(name='a'),
                    mock_tag(name='b')
                ]
            )
        ]

        expected = MockTag(name='parent')
        expected.children = [
            MockTag(name='a'),
            MockTag(name='b'),
            MockTag(name='a'),
            MockTag(name='b')
        ]

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_span_5(self):
        template = mock_tag(name='parent')[
            scope.span,
        ]

        expected = MockTag(name='parent')
        expected.children = []

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_span_6(self):
        template = mock_tag(name='parent')[
            scope.span[
                scope.span
            ]
        ]

        expected = MockTag(name='parent')
        expected.children = []

        self.assertEqual(scope.flatten(template), expected)

    def test_tag_indent_3(self):
        template = mock_tag(name='parent')[
            scope.span[
                mock_tag(name='a'),
                scope.indent[
                    mock_tag(name='b'),
                    mock_tag(name='c')
                ],
                mock_tag(name='d')
            ],
        ]

        expected = MockTag(name='parent')
        expected.children = [
            MockTag(name='a'),
            scope.IndentTag().set_children([
                MockTag(name='b'),
                MockTag(name='c')
            ]),
            MockTag(name='d')
        ]

        self.assertEqual(scope.flatten(template), expected)

    def test_serialization_1(self):
        template = mock_tag(name='element')

        expected = 'element\n'

        self.assertEqual(scope.serialize(template), expected)

    def test_serialization_2(self):
        template = mock_tag(name='parent')[
            mock_tag(name='child-1'),
            mock_tag(name='child-2')
        ]

        expected = 'parent\n    child-1\n    child-2\n'

        self.assertEqual(scope.serialize(template), expected)

    def test_serialization_3(self):
        template = mock_tag(name='element')

        expected = 'element\n'

        self.assertEqual(scope.serialize(scope.flatten(template)), expected)

    def test_serialization_4(self):
        template = mock_tag(name='parent')[
            mock_tag(name='child-1'),
            scope.indent[
                mock_tag(name='child-2')
            ]
        ]

        expected = 'parent\n    child-1\n        child-2\n'

        self.assertEqual(scope.serialize(template), expected)

    def test_serialization_5(self):
        template = mock_tag(name='parent')[
            mock_tag(name='child-1'),
            '',
            scope.indent[
                'str:child-2'
            ]
        ]

        expected = 'parent\n    child-1\n    \n        str:child-2\n'

        self.assertEqual(scope.serialize(template), expected)

    def test_serialization_6(self):
        template = mock_tag(name='parent')[
            mock_tag(name='child-1'),
            scope.new_line,
            scope.indent[
                'str:child-2'
            ]
        ]

        expected = 'parent\n    child-1\n\n        str:child-2\n'

        self.assertEqual(scope.serialize(template), expected)

    def test_serialization_7(self):
        options = scope.SerializerOptions()
        options.indentation_character = '\t'
        options.indentation_factor = 1

        template = mock_tag(name='parent')[
            mock_tag(name='child-1'),
            scope.new_line,
            scope.indent[
                'str:child-2'
            ]
        ]

        expected = 'parent\n\tchild-1\n\n\t\tstr:child-2\n'

        self.assertEqual(scope.serialize(template, options), expected)


class TestCppSerializer(unittest.TestCase):  # pylint: disable-msg=R0904
    def test_cpp_serializer_1(self):
        template = cpp.tfile[
            '#include <string>'
        ]

        expected = """#include <string>\n"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_2(self):
        template = cpp.tfile[
            cpp.tclass('Foo')
        ]

        expected = """class Foo {\n}; // class Foo\n"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_3(self):
        template = cpp.tfile[
            cpp.tclass(
                'Foo',
                superclasses=[(cpp.PUBLIC, 'Bar'), (cpp.PRIVATE, 'Baz')]
            )
        ]

        expected = """class Foo : public Bar, private Baz {
}; // class Foo
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_4(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('Foo')[
                cpp.tclass('Bar')
            ]
        ]

        expected = """
class Foo {
    class Bar {
    }; // class Bar
}; // class Foo
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_5(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('Foo')[
                cpp.tclass('Bar'),
                cpp.tclass('Baz', visibility=cpp.PUBLIC)
            ]
        ]

        expected = """
class Foo {
    class Bar {
    }; // class Bar
public:
    class Baz {
    }; // class Baz
}; // class Foo
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_6(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('Foo'),
            cpp.tclass('Bar')
        ]

        expected = """
class Foo {
}; // class Foo
class Bar {
}; // class Bar
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_7(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tnamespace('Baz')[
                cpp.tclass('Foo'),
                cpp.tclass('Bar')
            ]
        ]

        expected = """
namespace Baz {
    class Foo {
    }; // class Foo
    class Bar {
    }; // class Bar
} // namespace Baz
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_8(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tnamespace('A'),
            cpp.tnamespace('B')
        ]

        expected = """
namespace A {
} // namespace A
namespace B {
} // namespace B
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_9(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tstruct('Foo')[
                cpp.tstruct('Bar')
            ]
        ]

        expected = """
struct Foo {
    struct Bar {
    }; // struct Bar
}; // struct Foo
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_10(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tstruct('Foo')[
                cpp.tstruct('Bar'),
                cpp.tstruct('Baz', visibility=cpp.PRIVATE)
            ]
        ]

        expected = """
struct Foo {
    struct Bar {
    }; // struct Bar
private:
    struct Baz {
    }; // struct Baz
}; // struct Foo
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_11(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tnamespace
        ]

        expected = """
namespace {
} // namespace
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_12(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo')
        ]

        expected = """
void foo() {}
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_13(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo', ['int a'])
        ]

        expected = """
void foo(int a) {}
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_14(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo', ['int a', 'string b'])
        ]

        expected = """
void foo(int a, string b) {}
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_15(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo', ['int a', 'string b'],
                        virtual=True, const=True)
        ]

        expected = """
virtual void foo(int a, string b) const {}
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_16(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('int', 'foo')[
                'return 42;'
            ]
        ]

        expected = """
int foo() {
    return 42;
}
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_17(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tmethod('int', 'foo')
            ]
        ]

        expected = """
class A {
    int foo() {}
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_18(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tmethod('int', 'foo', visibility=cpp.PUBLIC)
            ]
        ]

        expected = """
class A {
public:
    int foo() {}
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_19(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tattribute('int', 'var')
            ]
        ]

        expected = """
class A {
    int var;
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_20(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tattribute('int', 'var', visibility=cpp.PUBLIC,
                               const=True)
            ]
        ]

        expected = """
class A {
public:
    const int var;
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_21(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tctor('A', visibility=cpp.PUBLIC)[
                    '// do nothing'
                ],
                cpp.tctor('A', ['const A & other'])
            ]
        ]

        expected = """
class A {
    A(const A & other) {}
public:
    A() {
        // do nothing
    }
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_22(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tclass('A')[
                cpp.tdtor('~A', virtual=True)
            ]
        ]

        expected = """
class A {
    virtual ~A() {}
}; // class A
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_23(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tenum('A', ['B', 'C', 'D'])
        ]

        expected = """
enum A {
    B,
    C,
    D
};
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_24(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tenum('A', [])
        ]

        expected = """
enum A {};
"""

        self.assertEqual(scope.serialize(template), expected)

    def test_cpp_serializer_25(self):
        template = cpp.tfile[
            scope.new_line,
            cpp.tmethod('void', 'foo', ['int a', 'string b'],
                        implemented=False)
        ]

        expected = """
void foo(int a, string b);
"""

        self.assertEqual(scope.serialize(template), expected)

if __name__ == '__main__':
    unittest.main()
