# Introduction to Pyotr

**Pyotr** is a Python library for serving and consuming REST APIs based on [OpenAPI](https://swagger.io/resources/open-api/) specifications. Its name is acronym of "Python OpenAPI to REST".

The project consists of two separate libraries that can be used independently:

* `pyotr.server` is a [Starlette](https://www.starlette.io)-based framework for serving OpenAPI-based services. It is functionally very similar to [connexion](https://connexion.readthedocs.io), except that it aims to be fully [ASGI](https://asgi.readthedocs.io)-compliant. 
* `pyotr.client` is a simple HTTP client for consuming OpenAPI-based services. It is a spiritual descendent of the
 [Bravado](https://github.com/Yelp/bravado) library, which currently supports only Swagger 2.0.

**WARNING:** This is still very much work in progress and not nearly ready for any kind of production.

Why Pyotr?
----------

The main advantage of Pyotr -- both as a server and as a client -- is that it uses the OpenAPI specification to both prepare and validate requests and responses. 

Specifically, when `pyotr.server` receives a request it validates it against the URLs defined in the specification
, raising an error in case of an invalid request. On a valid request it looks for an "endpoint function" matching the
 request URL's `operationId`; this function is supposed to process a request and return a response, which is then
  also validated based on the specification rules before being sent back to the client.
  
On the other hand, `pyotr.client` uses the `operationId` to generate a request based on the rules defined in the
 specification. The user simply needs to call the `operationId` as if it was a method of a client instance
 , optionally passing any specified arguments. 
