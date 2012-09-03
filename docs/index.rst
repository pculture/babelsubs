.. babelsubs documentation master file, created by
   sphinx-quickstart on Mon Sep  3 11:55:09 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to babelsubs's documentation!
=====================================

Babelsubs is a Python library that helps you to convert from one subtitle
format to another.

Example usage:

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

    from babelsubs.generators import SRTGenerator
    from babelsubs import load_from

    parsed = load_from(dxfp_data, type='dfxp').to_internal()
    srt_output = unicode(SRTGenerator(parsed))
    print srt_output

This will output:

::

    1
    00:00:00,039 --> 00:00:00,040
    With end



Contents:

.. toctree::
   :maxdepth: 2
