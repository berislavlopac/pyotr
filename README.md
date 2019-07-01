Pyotr
=====

**Pyotr** is a Python library for serving and consuming REST APIs based on [OpenAPI](https://swagger.io/resources/open-api/) specifications. Its name is acronym of "Python OpenAPI to REST".

The project consists of two separate libraries that can be used independently:

* `pyotr.server` is a [Starlette](https://www.starlette.io)-based framework for serving OpenAPI-based services. It is functionally very similar to [connexion](https://connexion.readthedocs.io), except that it aims to be fully [ASGI](https://asgi.readthedocs.io)-compliant. 
* `pyotr.client` is a simple HTTP client for consuming OpenAPI-based services.

**WARNING:** This is still very much work in progress and not nearly ready for any kind of production.


Quick Start
-----------

### Server

    from pyotr.server import Application
    
    app = Application.from_file("path/to/openapi.yaml", "path.to.endpoints.module")
    
### Client

    from pyotr.client import Client
    
    client = Client.from_file("path/to/openapi.yaml")
    result = client.some_endpoint_id("path", "variables", "query_var"="example")
    
Why Pyotr?
----------

The main advantage of Pyotr -- both as a server and as a client -- is that it uses the OpenAPI specification to both prepare and validate requests and responses.

In `pyotr.server`, the specification is used to route a request to the right endpoint, allowing the developer to simply implement the endpoint function. And for `pyotr.client`, the spec is used to construct the request, applying any arguments provided by the user, before sending it to the server.
