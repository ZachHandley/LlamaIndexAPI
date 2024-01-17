from PIL import Image
from appwrite.input_file import InputFile
from io import BytesIO
import aiohttp
import base64
from mimetypes import guess_extension
from datetime import datetime

from app.models.models import ImageIngestionRequest


def image_to_inputfile(image: str, filename: str, mimetype: str) -> InputFile:
    """
    Convert a base64 encoded image to an InputFile object.

    Args:
        image (str): The base64 encoded image.
        filename (str): The filename of the image.
        mimetype (str): The MIME type of the image.

    Returns:
        InputFile: The InputFile object created from the image.
    """
    image_bytes = base64.b64decode(image)
    return InputFile.from_bytes(
        bytes=image_bytes, filename=filename, mime_type=mimetype
    )


def pil_image_to_base64(image: Image.Image) -> str:
    """
    Convert a PIL Image object to a base64 encoded string.

    Args:
        image (Image.Image): The PIL Image object.

    Returns:
        str: The base64 encoded string of the image.
    """
    image_buffer = BytesIO()
    image.save(image_buffer, format="JPEG")
    return base64.b64encode(image_buffer.getvalue()).decode()


async def fetch_image_from_url(image_url: str) -> bytes | None:
    """
    Fetch an image from a given URL.

    Args:
        image_url (str): The URL of the image.

    Returns:
        bytes | None: The image data in bytes if successful, None otherwise.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                image_data = await response.read()
                return image_data
    return None


async def image_req_to_base64(
    image_request: ImageIngestionRequest,
) -> bytes | None:
    """
    Convert an ImageIngestionRequest to a base64 encoded string.

    Args:
        image_request (ImageIngestionRequest): The ImageIngestionRequest object.

    Returns:
        bytes | None: The base64 encoded string of the image if successful, None otherwise.
    """
    if image_request.image_url is not None:
        print(f"Image URL is not None")
        image_data = await fetch_image_from_url(image_request.image_url)
        if image_data is not None:
            image = Image.open(BytesIO(image_data))
            return pil_image_to_base64(image).encode()
    elif image_request.image is not None:
        if isinstance(image_request.image, str):
            print(f"Image is a string")
            return image_request.image.encode()
        else:
            # This means it's Base64 Encoded
            return image_request.image
    else:
        return None


def get_image_filename(image_request: ImageIngestionRequest) -> str:
    """
    Get the filename of an image from an ImageIngestionRequest.

    Args:
        image_request (ImageIngestionRequest): The ImageIngestionRequest object.

    Returns:
        str: The filename of the image.
    """
    file_extension = guess_extension(image_request.mimetype)
    filename = (
        f"{image_request.userId}_{datetime.now().timestamp()}{file_extension}"
    )
    return filename
