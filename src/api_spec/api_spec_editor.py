from fastapi.openapi.utils import get_openapi
import re
import json


# The description field of the api spec is compatible with readme syntax
description = """
Work In Progress (WIP)
"""


def set_openapi_spec(openapi_schema, routes):
    if openapi_schema:
        return openapi_schema

    openapi_schema = get_openapi(
        title="Database Service",
        version="0.1",
        # summary="This is a very custom OpenAPI schema",
        description=description,
        routes=routes,
    )

    # openapi_schema = change_to_FileUploadModel(openapi_schema)

    return openapi_schema