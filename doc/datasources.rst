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
| metric                            | Target                                  |
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

Opentsdb
--------

