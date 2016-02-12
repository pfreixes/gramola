.. _data-sources:

Data Sources
===============

Each time serie data base implementation uses diferents params to build datasources
configurations or to perform metrics queries. Although few fields are shared between
the diffent implementations. The `type` and the `name` fields are used by all 
datasources and the `metric` field is used by all queries.

The following tables belonging to each time serie data base implementation lists the
params, required arguments, and the options params accepted by each implementation.

As we see in the previous chapters this fields are used by the command interface or
by the programmatic interface of gramola. 

Graphite
--------

Datasource
~~~~~~~~~~

+-----------------------------------+-----------------------------------------+
| Param                             | Descripiton                             |
+===================================+=========================================+
| type                              | Always get the `grahpite` value         |
+-----------------------------------+-----------------------------------------+
| name                              | Name of the datasource                  |
+-----------------------------------+-----------------------------------------+
| url                               | Url of the service, for exampl          |
|                                   | `http://localhost:9000`                 |
+-----------------------------------+-----------------------------------------+

Query
~~~~~

+-----------------------------------+-----------------------------------------+
| Param                             | Descripiton                             |
+===================================+=========================================+
| target                            | Target                                  |
+-----------------------------------+-----------------------------------------+

+-----------------------------------+-----------------------------------------+
| Option                            | Descripiton                             |
+===================================+=========================================+
| since                             | Get values from, default -1h            |
+-----------------------------------+-----------------------------------------+
| until                             | Get values until, default now           |
+-----------------------------------+-----------------------------------------+


CloudWatch
-----------

Datasource
~~~~~~~~~~

+-----------------------------------+-----------------------------------------+
| Param                             | Descripiton                             |
+===================================+=========================================+
| type                              | Always get the `cw` value               |
+-----------------------------------+-----------------------------------------+
| name                              | Name of the datasource                  |
+-----------------------------------+-----------------------------------------+

+-----------------------------------+-----------------------------------------+
| Option                            | Descripiton                             |
+===================================+=========================================+
| profile                           | Profile used insted of the default one, |
|                                   | usually stored in the aws config files  |
|                                   | ~/.aws/credentials and ~/.aws/config    |
+-----------------------------------+-----------------------------------------+
| region                            | Region used insted of the default one   |
|                                   | configured in the profile or if it is   |
|                                   | given as query argument.                |
+-----------------------------------+-----------------------------------------+

As an example the following command displays a CloudWatch datasource added to use
a specific profile and specific region:

.. code-block:: bash

    $ gramola datasourc-add-cw --region=eu-west-1 --profile=sandbox "test environment"
    Datasource `test environment` added
 
Query
~~~~~

+-----------------------------------+-----------------------------------------+
| Param                             | Descripiton                             |
+===================================+=========================================+
| metricspace                       | The metricspace name, ex: AWS/EC2       |
+-----------------------------------+-----------------------------------------+
| metricname                        | The metrics name, ex: CPUUtilization    |
+-----------------------------------+-----------------------------------------+
| dimensionname                     | Filter by this dimension name           |
+-----------------------------------+-----------------------------------------+
| dimensionvalue                    | Filter by this dimension value          |
+-----------------------------------+-----------------------------------------+

+-----------------------------------+-----------------------------------------+
| Option                            | Descripiton                             |
+===================================+=========================================+
| since                             | Get values from, default -1h            |
+-----------------------------------+-----------------------------------------+
| until                             | Get values until, default now           |
+-----------------------------------+-----------------------------------------+
| region                            | Use another region instead of the       |
|                                   | default one.                            |
+-----------------------------------+-----------------------------------------+
| statistics                        | Use another Statistic instead of the    |
|                                   | default one, values allowed : Average,  |
|                                   | Sum, Maximum, Minimum, SampleCount      |
+-----------------------------------+-----------------------------------------+

As an example the following command displays a query using a CloudWatch datasource where it get the CPU 
utilitzation of a specific EC2 instance:

.. code-block:: bash

    $ gramola query-cw --plot-maxx=20 --since=-3h --until=-2h cw AWS/EC2 CPUUtilization InstanceId i-61cefbec 
    |
    |
    |
    |
    |
    |
    |                                              **    *       *            **    *                      *
    |                                             ************************************************************
    +---+---+---+---+----+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
    min=0, max=6, last=5

Opentsdb
--------

