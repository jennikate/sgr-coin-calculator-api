# Notes, warning, errors to watch for etc.

```
 UserWarning: Multiple schemas resolved to the name Rank. The name has been modified. Either manually add each of the schemas with a different name or provide a custom schema_name_resolver.
 ```

 This seems to be due to the `partial=True` use.
 It's a warning, it doesn't stop the swagger doc being created and looking right.
 So I'm ignoring it for now.

 