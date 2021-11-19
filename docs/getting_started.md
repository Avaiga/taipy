# Getting Started with Taipy

## Installation

### Stable release

To install Taipy, run this command in your
terminal:

``` console
$ pip install taipy
```

This is the preferred method to install Taipy, as it will always install the most recent stable release.

If you don't have [pip][] installed, this [Python installation guide][]
can guide you through the process.

### From source

The source for Taipy can be downloaded from
the [Github repo][].

You can either clone the public repository:

``` console
$ git clone git://github.com/avaiga/taipy
```

Or download the [tarball][]:

``` console
$ curl -OJL https://github.com/avaiga/taipy/tarball/main
```

Once you have a copy of the source, you can install it with:

``` console
$ pip install .
```

  [pip]: https://pip.pypa.io
  [Python installation guide]: http://docs.python-guide.org/en/latest/starting/installation/
  [Github repo]: https://github.com/Avaiga/taipy
  [tarball]: https://github.com/Avaiga/taipy/tarball/main

## Creating a Taipy application

The general steps to take to create a Taipy application are the following:

   - Create the application setup

   - Create the application scenarios

   - Run the scenarios

   - Connect a user interface

   - Interact with the user interface

```
    import taipy
```
