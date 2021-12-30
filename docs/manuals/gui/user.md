# About

Taipy can generate a graphical user interface for you, if you need one.

## What is a graphical user interface

A graphical user interface is made of generated Web pages that are served by a Web server
hosted by the Taipy application itself (or on which the Taipy application relies). This
server and its settings are handled by the [`Gui object`](user_gui.md).

## How is the Graphical User Interface generated

The generated Web pages are build from a set of template text files that you provide,
where you would have planted placeholders to hold `_controls_`. Taipy comes the support
for two template formats, handled by the classes
[`Markdown`](../../reference/#taipy.gui.renderers.Markdown)
and [`Html`](../../reference/#taipy.gui.renderers.Html).

The basic principle is that you create pages as you need them, give them a name
so you can point your browser to show them, and add them to a `Gui` instance used in your application.

When the [`run() method`](../reference/#taipy.gui.gui.Gui.run) of the `Gui` instance
is invoked, a Web client can connect to the underlying server and request for a page.
At this time, Taipy transforms the page that you had created into some HTML content
that is sent to the client so the user can see the application interface.

!!! info "You can find more information on how pages are created and used in Taipy application in the [Pages](user_pages.md) section."
