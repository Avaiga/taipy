A series of toggle buttons that the user can select.

## Details

Toggle buttons can hold both some text and/or an image.

## Usage

### Simple

<code>
<|{value}|toggle|lov=Item 1;Item 2;Item 3|></code>
<code><|toggle|theme|></code>

### Advanced

<code><|{value}|toggle|lov={lov}|type=myType|adapter=lambda x: (x.id, x.name)|></code>

<br>or with properties<br>

<code><|{value}|toggle|properties={properties}|lov={lov}|></code>
