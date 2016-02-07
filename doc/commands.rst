Commands
============

Gramola comes with an unique shell entry point called *gramola* that supports several commands,
each one addressed to do a certain stuff. A *gramola* command execution gets a pattern like
*gramola <global options> command <command options> args*.

The global options are shared beteween all commands and allow us to modify the whole behaviour
of the gramola commands, the following list shows the global options supported:

  * **-v** Run the gramola command in verbose mode.
  * **-q** Run the gramola command in quite mode.
  * **--store** Use an alternative directory of the default one to grab the datasources and dashboards.

By default Gramola uses the user directory *~./gramola* to store there the datasources
and dashbaords saved by the user, this path can be override by the *--store* option.

The following sections explain each command grouped them into a three major sections : datasources,
queries and dashboards.

Because Gramola gives support for multiple time serie data bases, for those commands where
the interfaces are not fully shared between all interfaces, Gramola implements a sepecific
command for each implementation. This is the case for the command to add new datasources and for
the command to run queries.

Luckly the user can see the time serie data base related with one command just reading the command
name, for example the *datasource-add* command is expanded with as many cases as many implementations
there are, getting at last the following commands: *datasource-add-graphite*,
*datasource-add-cw*, *datasource-add-opentsdb* and so on.

The following sections use the *graphite* type for all commands, therefore to get a detailed list of those
arguments that belong to other time series data bases please take a look to the last section.

Datasources
-----------

Datasources are configurations of time serie data bases, a datasource explains to Gramola how it can
reach a specific service belonging to a time serie data base. All datasources have at least two fields
,independently of the kind of time serial database, the name of the data source and the type.

The **type** field is automatically handled by Gramola and it is collected automatically from the 
command name, therefore even this field is saved along with the other fields of the datasource the user
will not to take care of it.

The **name** field is the way to identify a datasource and it has to be unique, Gramola will not allow us 
to add duplicate name entries. The name of the datasource is used by other commands, such as the query command,
and the fields related with saved along with the name will be used to reach the servcie running behind this datasource.

Adding new data sources
~~~~~~~~~~~~~~~~~~~~~~~

Gramola gives the *datasource-add-graphite* command -remember that you have as many versions of the add 
command as many time serie databases are implemented- to add new data sources to the system. The following
snippet shows how we can use it to add a new one :

.. code-block:: bash

    $ gramola datasource-add-graphite "test datasource" http://localhost:9000
    Data source test failed, might the service not being available?
    THIS DATA SOURCE HAS NOT BE ADDED, use --no-test flag to add it even

The previous command **has not saved the datasource**, before the datasource is saved Gramola tries to
assert that there is service running and if it fails the datasource is not saved. If we want to save it
still, we have two options. Either we make sure that the service is running and it passes
the test or we can use the *--no-test* flag to skip the test step.

The following snippet shows how we can use the second option :

.. code-block:: bash

    $ gramola datasource-add-graphite --no-test "test datasource" http://localhost:9000
    Datasource `test datasource` added

Further we can use the *datasource-test* command to check if a data source is well configured and
test if the service behind it is running.

.. code-block:: bash

    $ gramola datasource-test "test datasource"
    Datasource `test datasource` FAILED!


Listing the data sources saved
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List the datasources that have been saved by the user before can be done throught to the
command *datasources-list*. As the following snippet shows it lists each datasource giving the
name and the type of each datasource:

.. code-block:: bash

    $ gramola datasource-list
    Datasource `test datasource` (graphite)
    Datasource `test2` (cw)
    Datasource `test3` (opentsdb)

Removing data sources
~~~~~~~~~~~~~~~~~~~~~

Remove a datasource can be also done using the *datasource-rm* command, it gets the name of the datasource
as a param and then it removes it from the Gramola store, take a look to the following snippet:

.. code-block:: bash

    $ gramola datasource-rm "test datasource"
    Datasource `test datasource` removed

Once a datasource has been removed it is not longer available for other `gramola` commands.

Query data sources
------------------

As was mentioned before, Gramola implements as many commands as many implementations there are, and to make
queries Gramola implements also an adhoc command for each data base. For example the following ones
are availables for each time serie data base  *query-graphite*, *query-cw*, etc.

So each time that we want to make a query we will use the properly command to run a compatible query for
the time serie data base. Although other options as those ones regarding the plot are the same used
by the all implementations.

A query command gets a pattern like *gramola <global options> query-graphite <plot options>
<query options> dashboard_name metric_name args*.

The plot options supported are:

  * **--refresh** Run the query for ever, by default *False*.
  * **--refresh-freq** When the refresh mode is enabled, refresh the plot at each X seconds. By default 5s.
  * **--plot-maxx** Give to the plot the maxium X value expected, otherwhise it will be relative to each query result.
  * **--plot-rows** Renderize the plot using a certain amount of rows, by default 8 rows.

Once the plot options has been given the command accepts either those optional params regarding each time serie
data base or those that are shared between all command args, to get more info about each param supported by
each time serie data base just take a look to the last section.

As a query options shared between all commands there is the *since* and the *until* options, both of them can be
used by all query commands. If they are not given they will take their default values, **-1h** for the *since*
param and **now** for the *until* param. It means that the query window time will involve the last hour.

Both options support different value formats as the following list describes:

    * **timestamp** A timestamp value such as *1454872083*
    * **iso8601** A datetime value that follows the ISO-8601 format such as *2016-02-15T23:59:59*
    * **now** Means the curent time.
    * **relative datetimes** A realative date time using the format *-(X)[min|h|d]* such as *-1min, -2h, 31d, ..*

As a mandatory arguments, a query command needs the name of the datasource to be used, the name of the metric to
query and at last other mandatory query arguments regarding the time serie data base.

The following snippet shows one example of the *query-graphite* command running a query to get the CPU load of a
specific webserver for the last one hour.


.. code-block:: bash

    $ gramola query-graphite --since=-1h --plot-maxx=100 --refresh --refresh-freq=10 grahpite webserver.CPU.total
    |                                                                                                            
    |                                                                                                            
    |                                         *                                                                  
    |                                         *                    *                                    *        
    |                                 *    *  *      * **          *    * *           *        *        *       *
    |                     * * * * **  *  * *  **  *  ****** *      *    * *    * * *  *        *     *  *    *  *
    |                  * ** ******** *** * * ******* ********** *  ** *** *** **** * **  *    ****   *  *** *** *
    |                  ************* ***** ******************** ** ********** ****** ** ** ******* ******** *****
    +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
    min=1, max=81, last=42

Because the refresh option has been given, the plot will refresh at each 5 seconds and moving the values from left
to right if there are new ones from the last call. The plot also warns about the minium, maxium and the
last value grabbed.


Dashboards
----------

TODO
