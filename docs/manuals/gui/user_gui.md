#GUI References

Here are the various configuration elements that you can set:

## Host

`host`

```py

(_str_, defaults to _"127.0.0.1"_)

```

## Port

`port`

The port number that the Web server uses.

```py

(_int_, defaults to _5000_)

```

## Title

`title`

The string displayed in the browser page title bar when navigating your Taipy application.

```py

(_str_, defaults to _"Taipy App"_)

```

## Favicon

`favicon`

The path to an image file what will be used as the page's icon when navigating your Taipy application.

```py

(_str_, defaults to the Avaiga logo)

```

## Dark mode

`dark_mode`

You can configure the initial theme mode of your application by simply setting this parameter to the value you prefer.

```py

(_bool_, defaults to _True_)

```

## Debug

`debug`

Set this to _True_ if you want to display the debug messages of the underlying Web server.

```py

(_bool_, defaults to _True_)

```

## Time Zone

`time_zone`

This parameter indicates how date and time values should be interpreted.

You can use a TZ database name (as listed in [Time zones list on Wikipedia](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)) or one of the following values: - _"client"_ indicates that the time zone to be used is the one of the Web client. - _"server"_ indicates that the time zone to be used is the one of the Web server.

```py

(_str_, defaults to _"client"_)

```

## Client URL

`client_url`

```py

(_str_, defaults to _"https:127.0.0.1:5000"_): TODO

```

## Theme

`theme`

```py

(_str_ or _None_, defaults to _None_):

```

## Use arrow

`use_arrow`

Can be set to _True_ in order to use the [Apache Arrow](https://arrow.apache.org/) technology to serialize data to Taipy clients. This allows for better performance in many situations.

```py

(_bool_, defaults to _False_)

```

## Browser notification

`browser_notification`

```py

(_bool_, defaults to _True_)

```

## Notification duration

`notification_duration`

The time, in milliseconds, that notifications should remain visible (see [Notifications](user_notifications.md) for details).

```py

(_int_, defaults to _3000_)

```

## Single client

`single_client`

Set to _True_ if only one client can connect and to _False_ if multiple clients can connect to this `Gui` instance.

```py

(_bool_, defaults to _False_)

```
