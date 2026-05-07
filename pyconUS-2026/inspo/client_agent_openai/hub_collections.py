"""Collections service client."""


import mimetypes

from pyscript_cloud.http import http_get, http_post
from pyscript_cloud.secrets import get_secret


def guess_mimetype(filename):
    """
    Guess the MIME type of a file based on its filename or extension.
    
    Args:
        filename (str): Path to the file or just the filename
        
    Returns:
        str: The guessed MIME type or 'application/octet-stream' if unknown
    """
    mimetype, encoding = mimetypes.guess_type(filename)

    # Return a default if the type couldn't be guessed
    return mimetype or 'application/octet-stream'


class Collections:
    def __init__(self, hub_api_key, api_url):
        self.hub_api_key = hub_api_key
        self.api_url = api_url
        
    async def create_collection(self, name, title):
        """Create a collection."""

        result = await http_post(
            self.API_URL, self.hub_api_key, dict(name=name, title=title)
        )

        return result
        
    async def write_file(self, collection_id, filename, content):
        """Write a file to a collection."""

        import js
        from pyscript.ffi import to_js
        
        try:
            # Create a Blob from the string content.
            blob = js.Blob.new([content], {type: "text/plain"})
            
            # Create a FormData object to send the file.
            form_data = js.FormData.new()
            form_data.append("files", blob, filename)

            options = {
                "method": "PUT",
                "headers": {
                    "Authorization": f"Bearer {self.hub_api_key}",
                },
                "body": form_data,
            }

            response = await js.fetch(
                self.API_URL + "/" + collection_id + "/files/" + filename, to_js(options)
            )

            if not response.ok:
                print(f"Error uploading file: {response.status} - {response.statusText}")
        
        except Exception as e:
             print(f"An error occurred: {e}")

        return response


    async def list(self):
        """List the user's collections."""
        
        result = await http_get(self.API_URL, self.hub_api_key)
        return result["items"]

    async def get_permissions(self, collection_id):
        """List the user's collections."""
        
        result = await http_get(
            self.API_URL + "/" + collection_id + "/permissions",
            self.hub_api_key
        )

        return result["items"]
