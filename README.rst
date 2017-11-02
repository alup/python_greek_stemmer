Greek Stemmer
-------------

This is a Python implementation of Skroutz's Ruby Greek stemmer.


Usage
=====

To use simply do:

    >>> from greek_stemmer import GreekStemmer
    >>> stemmer = GreekStemmer()
    >>> stemmer.stem('ΘΑΛΑΣΣΑ')


Installation
============

To install using pip issue the following command:

.. code-block:: bash

   pip install greek-stemmer


Testing
=======

In order to run the tests, you should firstly install all the necessary
dependencies:


.. code-block:: bash

   pip install -r requirements.txt

Tests can be run using the following command:


.. code-block:: bash

   python -m pytest tests/
