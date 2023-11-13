from Thymio import logger


class ThymioException(Exception):
    """
    Base class for Thymio Exceptions
    """
    def __init__(self, msg):
        """
        Create a ThymioException
        """
        logger.error(msg)
        super().__init__(msg)


class NoNodesException(ThymioException):
    """
    Exception raised when no nodes are found.
    """
    def __init__(self, node_name: str = None, msg: str = None):
        """
        Create a NoNodesException which by default will assume that there weren't any available. By specifying a node
        name, it changes the message to show that no nodes where found with a node name match.
        :param node_name: string of the name of the node to search for
        :param msg: override the exception message
        """
        self.node_name = node_name
        if msg:
            pass
        elif node_name:
            msg = f"No nodes found with name '{self.node_name}'."
        else:
            msg = "No nodes found."
        logger.error(msg)
        super().__init__(msg)