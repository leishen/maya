.. Maya documentation master file, created by
   sphinx-quickstart on Sun Dec 21 16:06:30 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Maya's documentation!
================================

Maya is a set of modules meant to ease experimentation with the Windows APIs using ctypes.

.. toctree::
   :maxdepth: 2

maya.ctypeshelper
=================
.. automodule :: maya.ctypeshelper
   :members:
   :undoc-members:

maya.winapi
===========

The winapi module contains useful (though not necessarily performant) implementations of common Windows API calls.

advapi32
--------
.. automodule :: maya.winapi.advapi32
   :members:
   :undoc-members:

kernel32
--------
.. automodule :: maya.winapi.kernel32
   :members:
   :undoc-members:

maya.winutils
=============

Contains useful, functional wrappers around the winapi module to make interacting with Windows more Pythonic.

security
--------
.. automodule :: maya.winutils.security
   :members:
   :undoc-members:

registry
--------
.. automodule :: maya.winutils.registry
   :members:

Examples
========


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

