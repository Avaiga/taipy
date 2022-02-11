A control that allows multiple selection and filtering on label.

## Usage

## Simple

<code><|{value}|tree|lov=Item 1;Item 2;Item 3|></code>

### Advanced

<code><|{value}|tree|lov={lov}|no filter|not multiple|type=myType|adapter=lambda x: (x.id, x.name, x.children)|></code>

or with properties

code><|{value}|selector|properties={properties}|lov={lov}|></code>
