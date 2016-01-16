Commands
============

Gramola comes with an unique shell entry point called `gramola` that supports several commands,
each one addressed to do a certain stuff. A gramola command execution gets a pattern like
`gramola <global options> command <command options> args`.

The the global options are shared beteween all commands and these options are just a few 
as the following list shows:

  * **-v** Run the gramola command in verbose mode.
  * **-q** Run the gramola command in quite mode.
  * **--store** Use an alternative directory of the default one to grab the datasources and dashboards.

By default `gramola` uses the user directory `~./gramola` to store there the datasources
and dashbaords saved by the user, this path can be override by the `--store` option.

The following sections explain each command grouped them into a three major sections : datasources,
queries and dashboards.

Because of `gramola` gives support for multiple time serie data bases for those commands where
the interfaces are not fully shared between all interfaces, `gramola` implements a sepecific
command for each implementation. This is the case for the command to add new datasources and for
the command to make queries.

Luckly the user can see the time serie data base related with one command just reading the type
name as a part of the command name, for example the datasource-add command is really expanded
with as many cases as many implementation there are, getting at last the following commands:
`datasource-add-graphite`, `datasource-add-cw`, `datasource-add-opentsdb` and so on.

The following sections uses the graphite commands flavor, therefore to get a detailed list of those
arguments that belong to other time series data bases please take a look to the last section.

Datasources
-----------

Datasources are configurations of time serie data bases that explain gramola can reach a specific
service. All datasources have at least two fields independently of the kind of time serial database,
the name of the data source and the type.

The **type** field is automatically handled by `gramola` and it is collected automatically from the 
command name, therefore even this field is saved along with the other fields of the datasource the user
will not to take care of it.

The **name** field is the way to identify a datasource and it has to be unique, `gramola` will not allow us 
to add duplicate entries. The name of the datasource is used by other commands, such as the query command,
and the fields related with it will be used to reach the servcie running behind this datasource.

Adding new data sources
~~~~~~~~~~~~~~~~~~~~~~~

Gramola gives the `datasource-add-graphite` command -remember that you have as many versions of the add 
command as many time serie databases are implemented- to add new data sources to the system. The following
snippet shows how we can use it to add a new one :

.. code-block:: bash

    $ gramola datasource-add-graphite "test datasource" http://localhost:9000
    Data source test failed, might the service not being available?
    THIS DATA SOURCE HAS NOT BE ADDED, use --no-test flag to add it even

The previous command **has not saved the datasource**, `gramola` tries to figure out if the configuration
given looks to an available service, and in the previous example the test failed. If we want to save it
still, we have two options. The first one, makes sure that the service is already there and it passes
the test, or the second one uses the `--no-test` flag to skip the test step.

The folloing snippet shows how we can use the second option :

.. code-block:: bash

    $ gramola datasource-add-graphite --no-test "test datasource" http://localhost:9000
    Datasource `test datasource` added

Further we can use the `datasource-test` command to check if a data source is well configured and
test if the service behind it is already running.

.. code-block:: bash

    $ gramola datasource-test "test datasource"
    Datasource `test datasource` FAILED!


Listing the data sources saved
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List the datasources that have been saved by the user before can be done throught to the
command `datasources-list`. As the following snippet shows it lists each datasource giving the
name and the type of each datasource:

.. code-block:: bash

    $ gramola datasource-list
    Datasource `test datasource` (graphite)
    Datasource `test2` (cw)
    Datasource `test3` (opentsdb)

Removing data sources
~~~~~~~~~~~~~~~~~~~~~

Remove a datasource can be also done using the `datasource-rm` command, it gets the name of the datasource
as a param and then it removes it from the `gramola` store, take a look to the following snippet:

.. code-block:: bash

    $ gramola datasource-rm "test datasource"
    Datasource `test datasource` removed

Once a datasource has been removed it is not longer available for other `gramola` commands.

Query data sources
------------------

TODO

Dashboards
----------

TODO
