# Prepare your application for deployment

To be able to deploy a Taipy application you should specify some options in your GUI.

These options will be provided from the environment with a default value to allow you to continue
to work locally without impact.

## Options

- **port:** Binding port for your application. By default, Taipy used the port `5000`.
- **client_url:** Url used to fetch data from the front end side. By default, Taipy used `localhost:5000`.
- **host:** Allows Taipy to listen to a public IP.

## Example

In a standard local Taipy application, you should have something that looks like
```python
# Your code

gui.run(title="Taipy Demo")
```
To be able to run in a remote environment, you should transform this line in
```python
import os

# Your code

gui.run(
    title="Taipy Demo",
    host='0.0.0.0',
    port=os.environ.get('PORT', '5000'),
    client_url=os.environ.get('CLIENT_URL', 'localhost:5000')
)
```
