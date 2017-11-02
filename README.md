# Vigilance

Vigilance is a simple command-line tool meant to ensure code quality metrics are met within codebases.

![Build status](https://travis-ci.org/belvedere-trading/vigilance.svg?branch=master)

## Quickstart

Vigilance can be installed from PyPi with `pip`.

```
pip install vigilance
```

The tool has a very simple interface:

```
vigilance --help
Usage: vigilance [OPTIONS]

  Runs Vigilance with the specified configuration file. The default
  configuration file if no options are passed is vigilance.yaml within the
  current working directory.

Options:
  --config FILENAME  Path to the vigilance configuration file
  --help             Show this message and exit.
```

All of Vigilance's functionality is controlled by the configuration file used by the tool. The configuration file defines:

1. The quality suites that must be verified
   * Analogous to code quality tools
2. The locations of the quality report for each suite
   * Contains the actual quality information for the codebase
3. The associated constraints that should be enforced upon the codebase
   * The metrics that a codebase must meet

These concepts will be explained more thoroughly later in the documentation.

If no configuration file is specified, Vigilance will look for a `vigilance.yaml` file in the current working directory.


For example, you could run Vigilance on its own code coverage report by calling the following set of command from the root of its source directory:

```
pip install .
pip install -r test_required_packages.req
python setup.py coverage
vigilance
```

If the quality enforcement succeeds, Vigilance will exit with a return code of 0; any other return code indicates a problem. A negative return code means that the tool failed while a positive code means that the quality metrics of the code base do not meet the configured constraints.

The configuration for Vigilance's own quality enforcement looks like:

```yaml
suites:
  cobertura:
    report: coverage.xml
    constraints:
      -
        type: global
        line: 80
        branch: 80
        complexity: 0
      -
        type: ignore
        paths:
          - vigilance/suite.py
      -
        type: file
        path: vigilance/constraint.py
        branch: 50
      -
        type: package
        name: vigilance
        branch: 75
  doxygen:
    report: doxygen.err
    constraints:
      -
        type: documentation
```

In this configuration file, we can see that two different quality suites have been defined: "cobertura" and "doxygen". These suite names must match the name of a quality suite (either built-in or from a plugin) known to Vigilance. Each suite defines the location of its quality report (the "report" key) and the constraints that the codebase must meet. For the "cobertura" suite, there are 4 total constraints defined. In the same order that they appear in the file, these are:

1. Globally, the codebase must have a line coverage of 80%, a branch coverage of 80%, and a complexity score of 0.
2. The file `vigilance/suite.py` should be ignored entirely from coverage enforcement.
3. The file `vigilance/constraint.py` is required to have a branch coverage of only 50% (rather than the global 80%).
4. The package `vigilance` is required to have a branch coverage of only 75% (rather than the global 80%). This stanza is equivalent to setting the global branch coverage constraint to 75%, but has been included as a sort of regression test.

Configuration file format changes depending on the type of quality report being inspected. For more detail about Vigilance configuration, please see the configuration section below.

## Configuring plugins

Vigilance ships with a dynamic plugin that allows users to make additional functionality available to the quality enforcement system. Plugins can be configured in one of three different locations:

1. The VIGILANCE_PLUGINS environment variable.
2. A `.vigilance` file within the directory in which Vigilance is run.
3. A `setup.cfg` file within the directory in which Vigilance is run.

The locations will be checked in that order and only the first location that contains information will be used. The actual plugin configuration is simply a comma-delimited list of plugins classes of the form `module.name:ClassName,other.module:AnotherPlugin`. If either of the available file sources, the files should be INI formatted, e.g.

```ini
[vigilance]
plugins = module.name:ClassName,other.module:AnotherPlugin
```

If the environment variable is used, the value of the variable should be the raw comma-delimited string.

## Concepts in detail

Before attempting to understand the implementation or configuraton details of Vigilance, it will be helpful to first understanding the conceptual model under which it operates. Vigilance models code quality enforcement into a few fundamental pieces:

* Quality reports (and their associated parsers), which are composed of
* Quality items, which must meet
* Quality constraints, which are defined by the user with
* Configuration stanzas

Please refer to the following sections for more detail about each of these concepts. Once the concepts are understood, the configuration file and authoring of Vigilance plugins should be fairly straightforward.

### Quality reports

Quality reports are the persisted output from an external code quality tool. Possible examples include code coverage reports, documentation generation output, or code complexity analysis. The quality report is how Vigilance gleans information about the quality of a codebase. For the remainder of the concepts documentation, we will consider a code coverage report as generated by [Cobertura](http://cobertura.github.io/cobertura/) (mainly because this is the coverage tool used to enforce code coverage on Vigilance's own codebase).

To make things a bit more concrete, this is a small snippet of what a Cobertura quality report might look like (pulled from a previous Vigilance coverage report):

```xml
<?xml version="1.0" ?>
<coverage branch-rate="0.8478" line-rate="0.9229" timestamp="1509394341434" version="4.0">
        <!-- Generated by coverage.py: https://coverage.readthedocs.org -->
        <!-- Based on https://raw.githubusercontent.com/cobertura/web/f0366e5e2cf18f111cbd61fc34ef720a6584ba02/htdocs/xml/coverage-03.dtd -->
        <sources>
                <source>/Users/jkaye/git/vigilance</source>
        </sources>
        <packages>
                <package branch-rate="0.825" complexity="0" line-rate="0.9102" name="vigilance">
                        <classes>
                                <class branch-rate="1" complexity="0" filename="vigilance/__init__.py" line-rate="1" name="__init__.py">
                                        <methods/>
                                        <lines>
                                                <line hits="1" number="4"/>
                                                <line hits="1" number="6"/>
                                                <line hits="1" number="7"/>
                                        </lines>
                                </class>
                                <class branch-rate="1" complexity="0" filename="vigilance/configuration.py" line-rate="0.9844" name="configuration.py">
                                ...
```

### Quality items

A quality report is conceptually nothing more than a collection of quality items. Each quality item is an individual data point that Vigilance is able to inspect and compare against the constraints configured by the user. For example, the interesting pieces from the quality report above are the `<package>` and `<class>` elements; therefore, these are the "quality items" that Vigilance will extract from the coverage report (actually, it's the default Cobertura plugin that performs this extraction, but we will get to that in more detail later).

Essentially, you can think of quality items as the pieces of data from a quality report that Vigilance will validate constraints against.

### Quality constraints

Quality constraints are the metrics that Vigilance will enforce against the quality items that it extracts from the quality report. Continuing with our code coverage example, possible constraints could be:

* Line coverage
* Branch coverage
* Cyclomatic complexity

As a user, we want line and branch coverage to remain high as our codebase changes through time, and complexity to remain low. These represent the constraints that Vigilance will enforce upon the codebase.

### Configuration stanzas

Finally, configuration stanzas are the means by which Vigilance determine's the user's desired constraints. The Vigilance configuration file has a fixed structure, but its dynamic value interpretation allows the tool to provide a significant amount of flexibility (provided that the plugins one uses are well written).

The configuration file that defines the aforementioned constraints for the coverage report looks like:

```yaml
suites:
  cobertura:
    report: coverage.xml
    constraints:
      -
        type: global
        line: 80
        branch: 80
        complexity: 0
      -
        type: ignore
        paths:
          - vigilance/suite.py
      -
        type: file
        path: vigilance/constraint.py
        branch: 50
      -
        type: package
        name: vigilance
        branch: 75
```

The individual stanzas are the list elements within the "constraints" key. Each stanza has at least a "type" key that defines the type of constraint that it is (within the context of the current plugin). The rest of the keys within each stanza are implementation specific; for this example, "line" and "branch" are minimum coverages (specified as percentages) while "complexity" is a maximum complexity score. Each of these constraints will be applied to the quality items extracted from the quality report based upon the type of its configuration stanza.

Please see the [plugin tooling section](#Tooling) for more information about how global/filtered constraints interact with one another.

## Plugins

All functionality from Vigilance is provided via plugins. Each plugin consists of four components (closely mapped to the concepts defined above) that together form a "quality suite". The suite contains everything that Vigilance requires to do its job:

1. A key. This is the unique name for the plugin that allows Vigilance to interpret the quality report and constraints from its configuration file
2. A report parser. This parses the textual representation of the quality report into Vigilance quality items
   * The report's associated quality items
3. Constraints.
4. Configuration stanzas.

### Default plugins

Vigilance comes with a set of default plugins that are automatically distributed along with its installation. Currently, the default plugins are:

* [Cobertura](https://github.com/belvedere-trading/vigilance/wiki/Cobertura)
* [Doxygen](https://github.com/belvedere-trading/vigilance/wiki/Doxygen)

### Writing a plugin

Once the Vigilance concepts are well understood, writing a new plugin is fairly straightforward. A plugin author will need to define:

1. The test metrics for their suite. These are the individual atoms of data that constraints will compare against quality items.
2. The [quality items](https://belvedere-trading.github.io/vigilance/classvigilance_1_1representation_1_1_quality_item.html) that comprise the quality report.
3. The [report parser](https://belvedere-trading.github.io/vigilance/classvigilance_1_1parser_1_1_parser.html) that parses the quality report.
4. The [constraints](https://belvedere-trading.github.io/vigilance/classvigilance_1_1constraint_1_1_constraint.html) that can be enforced.
5. The [configuration stanzas](https://belvedere-trading.github.io/vigilance/classvigilance_1_1configuration_1_1_configuration_stanza.html) that translate Vigilance configuration YAML into constraints.

Once the above have been defined, the entire quality suite can be assembled by defining a subclass of [AbstractPlugin](https://belvedere-trading.github.io/vigilance/classvigilance_1_1plugin_1_1_abstract_plugin.html). This subclass can then be made available to Vigilance's plugin system once the code is installed into the same Python environment as Vigilance itself.

The source of [the Cobertura plugin](https://github.com/belvedere-trading/vigilance/blob/master/vigilance/default_suites/cobertura.py) is a good place to start for an example of how to write a plugin of your own.

### Tooling

Vigilance contains a set of tools that make writing plugins a bit easier for users of the tool. These tools can be found in the [vigilance.plugin.tooling](https://belvedere-trading.github.io/vigilance/tooling_8py.html) module.

Currently, the tools available are a set of [ConfigurationStanza]() implementations that could be useful to many different types of plugins. The implementations can be broken down into two groups:

1. The global stanza
2. The filter stanzas

The global stanza (called [BaseStanza]() in the code) is meant to define the global quality metrics that should be applied to the codebase. This is the stanza that parses the "global" configuration key in the example configuration files above. The stanza accepts any constraint labels defined by the plugin's quality suite as keys and uses their corresponding values as the constraints. The filter stanzas share the same parsing functionality as the global stanza (actually, they derive from BaseStanza).

The key to the useful behavior between the filter/global stanzas lies in how the Vigilance enforcer decides which constraints should be applied to any given quality item. For each item, if any filter exists for a single constraint, only the filtered constraint will be applied. This makes it easy to configure many different permutations of quality metrics by defining multiple filters that override only one or two constraints applied to a subset of the codebase.

### API documentation

Full Doxygen documentation can be found at [the GitHub pages for this project](https://belvedere-trading.github.io/vigilance/).
