endpoint_name = {
    200: {
        "json" : "here"
    },
    # 202: {"description": "The document is being processed", "identifier": "uuid"},
    # 204: {"description": "No Content - No files provided or processed"},
    404: {"description": "Resource does not exist"},
    # 422: {
    #     "description": "Unprocessable content - File doesn't match the requirements"
    # },
    500: {"description": "Internal Server Error - Error during processing"},
}

second_endpoint = {}
