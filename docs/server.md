# Pyotr Server

Example Setup
-------------

The minimal setup consists of three files:

* a REST(ful) API specification in the form of an OpenAPI file, usually in YAML or JSON format
* a Python file, e.g. `server.py`, which initiates your application
* another Python file containing the individual endpoint functions

The directory `src/examples/server/` contains a working example Pyotr server application, using the specification at `src/examples/petstore.yaml` -- which is a copy of the standard OpenAPI [example specification](https://editor.swagger.io/). 

To run the example, follow these steps inside a Python `virtualenv`:

1. Install [`poetry`](https://poetry.eustace.io/docs/#installation)
2. Update `pyotr` dependencies: `poetry update`
3. Start the API server: `uvicorn examples.server.server:app --reload --host 0.0.0.0 --port 5000 --log-level debug`


Application
-----------

A Pyotr application is an instance of the `pyotr.server.Application` class, which is a subclass of `starlette.applications.Starlette`; this means it is fully ASGI-compatible and can be used as any other ASGI app.

When initialising a Pyotr server app, it is necessary to provide:

1. An OpenAPI specification.
2. Python module containing the endpoint functions.

For example:

    from pyotr.server import Application
    app = Application(spec=api_spec, base='path.to.endpoints')
    
The value of `spec` is either a Python dictionary of the OpenAPI spec, or an `openapi-core` `Spec` object. There is a helper class method which will load the spec provided a path to the specification file:

    app = Application.from_file(path='path/to/spec.yaml', base='path.to.endpoints')

The value of `base` is a dot-separated location of the Python module or package which contains the endpoint definitions; in the above example, it might be the file `path/to/endpoints.py` or the directory `path/to/endpoints/`. 


Endpoints
---------

The OpenAPI spec defines the endpoints ("paths") that the API handles, as well as the requests and responses it can recognise. Each endpoint has a [field](https://swagger.io/specification/#operation-object) called `operationId`, which is supposed to be globally unique; Pyotr takes advantage of this field to find the corresponding endpoint function.

When the app is started, it will look at all the `operationId` values in the spec and add a route for each of them. To locate the right endpoint functions, it imports the endpoint module combining the `base` argument and the `operationId` value, converting the function name to snake case if necessary. E.g. if the base is `path.to.endpoints` and the `operationId` is `fooBar`, it will import the `foo_bar` function located in either `path/to/endpoints.py` (or `path/to/endpoints/__init__.py`). Also, if the `operationId` value contains dots it will try to build the full path, so `some.extra.levels.fooBar` will look for the module `path/to/endpoints/some/extra/levels.py`.

An endpoint is a standard Python function, with the following requirements:

1. It doesn't have to be a coroutine function (defined using `async def` syntax), but it is highly recommended, especially if it needs to perform any asynchronous operations itself.
2. It needs to accept a single positional argument, a request object compatible with the Starlette [`Request`](https://www.starlette.io/requests/).
3. It has to return either a Python dictionary, or an object compatible with the Starlette [`Response`](https://www.starlette.io/responses/). If it is a dictionary, Pyotr will convert it into a Starlette `JSONResponse`.

A basic example of an endpoint function:

    async def get_pet_by_id(request):
        return {
            "id": request.path_params['id'],
            "species": "cat"
            "name": "Lady Athena",
        }
