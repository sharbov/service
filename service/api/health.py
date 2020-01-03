from connexion import NoContent


def get_health():
    """Health endpoint.

    Note:
        This method will be used continuously in order to determine
        if the service is up and running and ready to serve requests.

    """
    return NoContent, 204
