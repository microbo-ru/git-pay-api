# how to start api

```
cd api
export FLASK_APP=api.py FLASK_ENV=development

flask run
```

# OpenAPI (swagger) Generator
To generate API it's necessary to perform following steps:
1. Install the generator
```
> npm install @openapitools/openapi-generator-cli -g
```
2. Once you need to re-generate (the server) do the following operations:
```
> npx openapi-generator generate -i openapi.yaml -g python-flask
```
3. By the same way a client proxy could be also generated
```
> npx openapi-generator generate -i openapi.yaml -g typescript-axios
```