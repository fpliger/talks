"""Tools for use in LLM conversations."""


from hub import Hub, tool


@tool(
    description="Get the smell of a location",
    inputs=[
        dict(name="location", type=str, description="The city and state, e.g. San Francisco, CA")
    ]
)
async def smells_like(location):
    import random
    return {"smell": random.choice(["roses", "old socks", "soggy newspapers"])}



@tool(
    description="""
    
    List my collections.
    
    """,
    inputs=[]
)
async def list_collections():
    result = await Hub.instance.collections.list()
    return {"message": "success", "collections": result}


@tool(
    description="""
    
    Check if a collection with the given `collection_name` exists.

    Return the collection Id if it exists, otherwise None.

    
    """,
    inputs=[
        dict(name="collection_name", type=str, description="The name of the collection"),
    ]
)
async def check_if_collection_exists(collection_name):
    result = await Hub.instance.collections.list()
    for collection in result:
        if collection["name"] == collection_name:
            return {"collection_id": collection["id"]}

    return {"collection_id": None}


@tool(
    description="""
    
    Create a collection with the given `collection_name`.

    Check if the collection already exists and if it does, don't create it.

    Return the `collection_id` of the newly created collection.
    
    """,
    inputs=[
        dict(name="collection_name", type=str, description="The name of the collection to create"),
    ]
)
async def create_collection(collection_name):
    result = await Hub.instance.collections.create_collection(
        name=collection_name, title=collection_name
    )

    return {"message": "success", "collection_id": result["id"]}


@tool(
    description="""
    
    Add a file to a collection with the given Id in `collection_id`.

    If the collection doesn't exist then create it first.
    
    """,
    inputs=[
        dict(name="collection_id", type=str, description="The Id of the collection to add the file to"),
        dict(name="filename", type=str, description="The name of the file to add"),
        dict(name="content", type=str, description="The contents of the file to add"),
    ]
)
async def add_file_to_collection(collection_id, filename, content):
    result = await Hub.instance.collections.write_file(
        collection_id, filename, content
    )
    
    return {"message": "success"}


@tool(
    description="""
    
    Get the permissions for on collection.

    """,
    inputs=[
        dict(name="collection_id", type=str, description="The Id of the collection to add the file to"),
    ]
)
async def get_collection_permissions(collection_id):
    result = await Hub.instance.collections.get_permissions(
        collection_id
    )

    print("Getting permissions", collection_id, result)

    formatted_permissions = [
        f"""
        Permission: {permission['type']}
        Relation: {permission['relation']}
        Id: {permission['id']}
        """

        for permission in result
    ]
    
    return "# Permissions\n---\n".join(formatted_permissions)
