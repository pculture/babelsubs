Welcome to babelsubs's documentation!
=====================================

Babelsubs is a Python library that helps you to convert from one subtitle
format to another.

Installation
------------

Via pip:

::

    $ pip install -e git+https://github.com/pculture/babelsubs.git#egg=babelsubs

.. note:: Once the library reaches a stable state, it will be published to
    PyPI.

Via distutils:

::

    $ git clone git://github.com/pculture/babelsubs.git
    $ cd babelsubs
    $ python setup.py install


Usage
-----

.. code-block:: python

    dxfp_data = """<?xml version="1.0" encoding="UTF-8"?>
    <tt xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:ttm="http://www.w3.org/ns/ttml#metadata">
        <head>
            <metadata>
                <ttm:title>Just a test file</ttm:title>
            </metadata>
            <styling>
                <style tts:fontSize="12" tts:fontFamily="Verdana" tts:backgroundColor="black" xml:id="s1" tts:fontWeight="normal" tts:fontStyle="normal" tts:textAlign="center" tts:color="yellow"></style>
            </styling>
        </head>
        <body>
            <div style="s1" xml:id="d1">
                <p xml:id="p3" begin="00:00:39.667" end="00:00:40.300"> With end </p>
            </div>
        </body>
    </tt>"""

    from babelsubs import load_from

    print load_from(dxfp_data, type='dfxp').to("srt")

This will output:

::

    1
    00:00:00,039 --> 00:00:00,040
    With end

Supported formats
-----------------

* dfxp
* sbv
* srt
* ssa
* ttml
* txt
* json
