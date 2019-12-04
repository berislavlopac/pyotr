Pyotr
=====

[![Documentation Status](https://readthedocs.org/projects/pyotr/badge/?version=latest)](https://pyotr.readthedocs.io/en/latest/?badge=latest)
[![CI builds](https://b11c.semaphoreci.com/badges/pyotr.svg?style=shields)](https://b11c.semaphoreci.com/badges/pyotr.svg?style=shields)

**Pyotr** is a Python library for serving and consuming REST APIs based on 
[OpenAPI](https://swagger.io/resources/open-api/) specifications. Its name is acronym of "Python OpenAPI to REST".

The project consists of two separate libraries that can be used independently:

* `pyotr.server` is a [Starlette](https://www.starlette.io)-based framework for serving OpenAPI-based services. 
  It is functionally very similar to [connexion](https://connexion.readthedocs.io), except that it aims to be fully 
  [ASGI](https://asgi.readthedocs.io)-compliant. 
* `pyotr.client` is a HTTP client for consuming OpenAPI-based services.

**WARNING:** This is still very much work in progress and not quite ready for production usage. Until version 1.0 is 
released, any version can be expected to break backward compatibility.


Quick Start
-----------

### Server

    from pyotr.server import Application
    from some.path import endpoints
    
    app = Application.from_file("path/to/openapi.yaml", module=endpoints)
    
### Client

    from pyotr.client import Client
    
    client = Client.from_file("path/to/openapi.yaml")
    result = client.some_endpoint_id("path", "variables", "query_var"="example")
