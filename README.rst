Gramola
=======

Gramola is a console port of Grafana_ that uses console plots to render time series data points. Because sometimes we need
a quick view of one metric for debuging propouses, or just because the numbers doesn't matter and our concern is about
how the metric behaves, Gramola gives us a easy, fast and polyglot data source implementation to make it.

Gramola spports data sources such as Graphite and CloudWatch, but other time series data bases can be implemented
eaasly.

Quick guide
-----------

Gramola allows us to query the datapoints belonging one metric from one specific service with just one line, the following
snippet shows how it can be done:

.. code-block:: bash

    $ gramola datasource-echo-graphite http://localhost:9000 | gramola query-graphite - server.web1.load
                              *                                                                  
                              *                                                                  
                              *                                                                  
                           *  *               *               **         *                       
       *                   *  *               *               **       * *                       
       *  * *           *  *  *        *   *  *      * *  *   ***     ** ** *     * **           
       ** * *  *        *  * **  *     *   *  * *    * *  *   ***     ** ** *     * **     *    *
       **** *  **       *  * **  *     *   * ** *    * * **   ***  * *** ** *    ***** * ********
       **** *  *****  ***  ***** **    * * **** *    *** **   ***  ***** ** *** *****************
       ******  ****** **** ********    **********   ******** *********** ** *********************
    ---------------------------------------------------------------------------------------------
    min=0, max=100, last=45


But usually we want to save our datasources to be used further by further queries. Gramola allows us to save data sources as 
the following snippet shows:

.. code-block:: bash

    $ gramola datasource-add-graphite "Graphite localhost" http://localhost:9000
    Datasource `Graphite localhost` added

Then the data sources is always available and can be used to query your metrics. To get more info about Gramola and how 
its features can be used read the full documentation `here <doc/index.rst>`_
