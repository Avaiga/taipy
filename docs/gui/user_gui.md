# The `Gui` object

## Initializing

## Configuration

Here are the various configuration elements that you can set:

  - `host` (_str_, defaults to _"127.0.0.1"_)
  - `port` (_int_, defaults to _5000_): The port number that the Web server uses.
  - `title` (_str_, defaults to _"Taipy App"_): The string displayed in the browser page title
    bar when navigating your Taipy application.
  - `favicon` (_str_, defaults to the Avaiga logo): The path to an image file what will be used
    as the page's icon when navigating your Taipy application.
  - `dark_mode` (_bool_, defaults to _True_): You can configure the initial theme mode
    of your application by simply setting this parameter to the value you prefer.
  - `debug` (_bool_, defaults to _True_): Set this to _True_ if you want to display the
    debug messages of the underlying Web server.
  - `time_zone` (_str_, defaults to _"client"_): This parameter indicates how date and time
     values should be interpreted.  
     You can use a TZ database name (as listed in
     [Time zones list on Wikipedia](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))
     or one of the following values:
     - _"client"_ indicates that the time zone to be used is the one of the Web client.
     - _"server"_ indicates that the time zone to be used is the one of the Web server.
  - `client_url` (_str_, defaults to _"https:127.0.0.1:5000"_): TODO
  - `theme` (_str_ or _None_, defaults to _None_): 
  - `use_arrow` (_bool_, defaults to _False_): Can be set to _True_ in order to use the
    [Apache Arrow](https://arrow.apache.org/) technology to serialize data to Taipy
    clients. This allows for better performance in many situations.
  - `browser_notification` (_bool_, defaults to _True_): 
  - `notification_duration` (_int_, defaults to _3000_): The time, in milliseconds, that
    notifications should remain visible (see [Notifications](user_notifications.md) for
    details).
  - `single_client` (_bool_, defaults to _False_): Set to _True_ if only one client can connect and to _False_ if multiple clients can connect
    to this `Gui` instance.
