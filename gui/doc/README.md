# Taipy visual elements documentation

Taipy visual elements are React components that are created
after they were defined from Python code.

What is exposed to the programmer is the set of properties that
each visual element understands. This directory contains all it
needs to generate the functional documentation for Taipy programmers
to use.

For each visual component, you need to provide or update two files:

   - `<element_name>.csv`: the list of all properties, in the order you
     want them to appear in the visual element documentation page.

     This CSV file (that you can edit using Excel or even a text editor)
     must have the following header: `Name,Type,Default,Doc`.

     And the following rules apply on the different columns:

     - _Name_: the name of the property.

       If the property is the default property, you must prefix the property name
       with a star (*) symbol.

     - _Type_: the type of this property.

       If the property accepts several types, you can separate the type names with a
       vertical bar (|) character.

       If the type is a dictionary, make sure you indicate the expected types
       for both the key and value.

       If the property is dynamic, it should be reflected by surrounding the type
       (or sequence of type names) by `dynamic(...)`.

     - _Default_: the default value for this property.

       If there is no default value, this cell must be empty.

       If the default value is a Boolean, do not bother with the way
       Excel enforces the capital TRUE or FALSE. The process ensures
       that it appears as the Python True or False to the user.

     - _Doc_: The actual documentation for this property.

       You can have a multi-line cell (use Alt-Enter on Excel).

You cannot use any Markdown in the CSV content. You must use raw HTML.

If your element inherits some property interfaces (like _shared_), you must
add them in the property name, prefixed by the '>' sign (ex.: `>shared`).

   - All the properties of the interface will be listed as properties
     of the visual element.
   - If you need to have an inherited property appear elsewhere in the
     property list:
      - declare it where you need it to appear in the property
        list, with the same name (and potentially the '*' prefix if
        it is the default property for that element).
      - set the '_Type_' value to '<' to simply copy all the inherited
        property fields.
