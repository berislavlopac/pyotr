# Pyotr Client

Pyotr client has kind of an opposite approach from the server: it allows a user to call an `operationId` as if it was a Python method.

Basic Usage
-----------

Pyotr client is a class that takes a dictionary or a `Spec` object; there is also a helper class method that will load the spec from a provided file:

    from pyotr.client import Client
    client = Client.from_file("path/to/openapi.yaml")
    
On instantiation, the client adds a number of methods to itself, each using a snake-case version of an `operationId` as a name. To make a request to the API, simply make call the corresponding method; e.g. if the spec contains an `operationId` named `someEndpointId`, it can be called as:
 
    result = client.some_endpoint_id("foo", "bar", query_var="example")

If the corresponding API endpoint accepts any path variables (e.g. `/root/{id}/{name}`), they can be passed in the form of positional arguments to the method call. Similarly, any query or body parameters can be passed as keyword arguments.

Pyotr client will validate both an outgoing request before sending it, as well as the response after receiving, to confirm that they conform to the API specification.

Advanced Usage
--------------

The `Client` class accepts four optional, keyword-only arguments on instantiation:

* `server_url`: A server hostname that will be used to make the actual requests. If it is not present in the `servers` list of the specification it will be appended, and if none is specified the first from the `servers` list will be used. 
* `client`: The HTTP client implementation used to make actual requests. By default Pyotr uses [`httpx`](https://www.encode.io/httpx/), but it can be replaced by any object compatible with the `Requests` client.
* `request_class`: The class an outgoing request will be wrapped into, before validation. By default it is the built-in `ClientOpenAPIRequest`; if additional functionality is needed it can be substituted by its subclass.
* `response_class`: The class an incoming response will be wrapped into, before validation. By default it is the built-in `ClientOpenAPIResponse`; if additional functionality is needed it can be substituted by its subclass.
