import base64


def base64_to_bytes(data) -> bytes:
    """
    Base64 encode a bytes object.
    :param data: A base64 string.
    :return: A bytes object.
    :rtype: bytes
    """
    return base64.b64decode(data)


def base64_to_string(data) -> str:
    """
    Base64 decode a string.
    :param data: A base64 string.
    :return: A base64 decoded string
    :rtype: str
    """
    return base64.b64decode(data.encode('utf-8')).decode('utf-8')


def bytes_to_base64(data) -> str:
    """
    Base64 encode a bytes object.
    :param data: A python bytes object.
    :return: A base64 encoded string
    :rtype: str
    """
    return base64.b64encode(data).decode('utf-8')


def string_to_base64(data) -> str:
    """
    Base64 encode a string.
    :param data: A python string.
    :return: A base64 encoded string
    :rtype: str
    """
    return str(base64.b64encode(data.encode()), 'utf-8')