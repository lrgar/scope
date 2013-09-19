# Scope

[![Build Status](https://travis-ci.org/lrgar/scope.png?branch=master)](https://travis-ci.org/lrgar/scope)

Scope is a library for creating code templates with pure Python code. Its goal is to allow to define a simple and clear structure for code templates, by offering a basic set of utilities that can be extended for providing language-specific constructs.

For this first release, it's provided a basic set for generating C++ code, but I will be extending to support more languages over time.

Scope is based in [Brevé][breve], a similar tool for generating HTML, and I created it so I can use it in another one of my projects, [spgen][spgen], but I intend to fully support the project.

[spgen]: https://github.com/lrgar/spgen
[breve]: http://breve.twisty-industries.com/

## Example

You can define a simple template as the following code, 

    import scope.lang.cpp as cpp
    import scope

    template = cpp.tfile [
    	'#include <string>',

        cpp.tclass(name='App') [
        	cpp.tattribute('std::string', '_name'),

            cpp.tmethod('std::string', 'GetName', visibility=cpp.PUBLIC, const=True) [
                'return this->_name;'
            ],

            cpp.tmethod('void', 'SetName', ['const std::string & value'], visibility=cpp.PUBLIC) [
                'this->_name = value;'
            ]
        ]
    ]

With the template you can just serialize it into a string with `scope.serialize(template)` and then print it or save it as a file. 

## Instalation

You can use `pip`,

    pip install scope

Or if you downloaded the source code then just call,

    python setup.py install

## Resources

- Go to the [Getting started][getting-started] page to see a simple guide of how you can use the library.
- After that, you can see the specifications for creating C++ code in the [C++ page][cpp-templates]

[getting-started]: https://github.com/lrgar/scope/wiki/Getting-started
[cpp-templates]: https://github.com/lrgar/scope/wiki/Cpp-templates

## License

This project is under the [MIT License](LICENSE.md).

## Changelog

- 0.1.0 - first release.