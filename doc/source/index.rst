.. Maya documentation master file, created by
   sphinx-quickstart on Sun Dec 21 16:06:30 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Maya's documentation!
================================

Maya is a set of modules meant to ease experimentation with the Windows APIs using ctypes.

.. toctree::
   :maxdepth: 2

Ctypeshelper
============
.. automodule :: ctypeshelper
   :members:
   :undoc-members:

winapi
======

The winapi module contains useful (though not necessarily performant) implementations of common Windows API calls.

advapi32
--------
.. automodule :: winapi.advapi32
   :members:
   :undoc-members:

kernel32
--------
.. automodule :: winapi.kernel32
   :members:
   :undoc-members:

winutils
========

Contains useful, functional wrappers around the winapi module to make interacting with Windows more Pythonic.

security
--------
.. automodule :: winutils.security
   :members:
   :undoc-members:

registry
--------
.. automodule :: winutils.registry
   :members:

Examples
========


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

