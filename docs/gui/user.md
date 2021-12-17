
# Creating your Graphical User Interfaces

Taipy can generate a graphical user interface for you, if you need one.

A graphical user interface is made of generated Web pages that are served by a Web server
hosted by the Taipy application itself (or on which the Taipy application relies). This
server and its settings are handled by the [`Gui` object](user_gui.md).

The generated Web pages are build from a set of template text files that you provide,
where you would have planted placeholders to hold _controls_. Taipy comes the support
for two template formats, handled by the classes
[`Markdown`](../../reference/#taipy.gui.renderers.Markdown)
and [`Html`](../../reference/#taipy.gui.renderers.Html).

The basic principle is that you create pages as you need them, give them a name
so you can point your browser to show them, and add them to a
[`Gui`](../../reference/#taipy.gui.gui.Gui) instance used in your application.  
When the [run() method](../../reference/#taipy.gui.gui.Gui.run) of the `Gui` instance
is invoked, a Web client can connect to the underlying server and request for a page.
At this time, Taipy transforms the page that you had created into some HTML content
that is sent to the client so the user can see the application interface.  
You can find more information on how pages are created and used in Taipy application
in the [Pages](user_pages.md) section.

Pages typically display textual information (like section titles), and Taipy also
lets you add _controls_: graphical element that can transform data into some display
that users are used to interpret (such as text areas, tables or charts).  
There are many different controls that can be used in any given page, and all are described
in the [Controls](controls.md) section.

Controls usually represent the value of some application variables, and can be updated by simply changing some variables value, as it is described in
[Binding variables](user_binding.md) section.

Interacting with controls usually trigger actions in the application code by means of invoking
functions that you have defined to process events coming from controls.  
We call such functions _callbacks_.The different callback types and when to use which
are described in the [Callbacks](user_callbacks.md) section.

Once you have your pages displaying what needs to be presented to the end-user,
you can always tune things a little bit by applying additional style. This lets
you bring better user experience by tweaking the appearance of the whole page content or 
individual controls.  
This is explained in details in the [Styling](user_styling.md) section.

At any time, you can raise a notification to the user, for example to indicate that some task
has been accomplished. These notifications can also appear as part of your machine's desktop
using the _Desktop Notifications_ feature. See [Notifications](user_notifications.md) for more details.

## [The `Gui` object](user_gui.md)
## [Pages](user_pages.md)
## [Controls](controls.md)
## [Binding variables](user_binding.md)
## [Callbacks](user_callbacks.md)
## [Styling](user_styling.md)
## [Notifications](user_notifications.md)
