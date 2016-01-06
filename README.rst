Gramola
=======

**STILL IN DEVELOPING, comming soon.**

Gramola is a console port of Grafana_ that uses sparklines_ to render time series data points. Because sometimes we need
a quick view of one metric for debuging propouses, or just because the numbers doesn't matter and our concern is about
how the metric behaves, Gramola gives us a easy, fast and polyglot data source implementation to make it.

Gramola main features can be resumed as:

    * Support for multiple data sources : Graphite, OpenTSDB, CloudWatch, InfluxDB, Prometheus.
    * Support for different outputs : sparkline, raw.
    * Support for dashboards.
    * Programatic access as a Python library.

Install
-------

Quick guide
-----------

Gramola allows us to query the datapoints belonging one metric from one specific service with just one line, the following
snippet shows how it can be done:

.. code-block:: bash

    $ gramola datasource-echo graphite http://localhost:9000 | gramola query - server.web1.load
    ▁▂▁▁▁▁▂▂▁▃▂▄█▃▁▂

But usually we want to save our datasources to be used further by further queries. Gramola allows us to save data sources as 
the following snippet shows:

.. code-block:: bash

    $ gramola datasource-add graphite http://localhost:9000 "Graphite localhost"
    Testing datasource ... Ok
    Added `Graphite localhost`, 1 datasources avaialbles now.

Then the data sources is always available and can be used to query your metrics.

.. code-block:: bash

    $ gramola query "Graphite localhost" server.web1.load
    ▁▂▁▁▁▁▂▂▁▃▂▄█▃▁▂

To get more info about Gramola and how its features can be used read the full documentation here

Developing
----------

.. _Grafana: http://grafana.org/
.. _sparklines: https://en.wikipedia.org/wiki/Sparkline


