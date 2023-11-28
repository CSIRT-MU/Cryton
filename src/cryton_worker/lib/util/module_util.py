from schema import Schema
import os

from cryton_worker.lib.util import exceptions
from cryton_worker.lib.util.util import Metasploit
from cryton_worker.lib.util.constants import OUTPUT, SERIALIZED_OUTPUT, RETURN_CODE


def get_file_binary(file_path: str) -> bytes:
    """
    Get a file binary content from path.
    :param file_path: Path to wanted file
    :return: Binary content of the desired file
    """
    with open(file_path, "rb") as bf:
        file_content = bf.read()

    return file_content


class File(object):
    """
    Wrapper class for Schema, adding support for file exists validation.
    """

    def __init__(self, *args, **kw):
        self._args = args
        if not set(kw).issubset({"error", "schema", "ignore_extra_keys"}):
            diff = {"error", "schema", "ignore_extra_keys"}.difference(kw)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self._error = kw.get("error")
        self._ignore_extra_keys = kw.get("ignore_extra_keys", False)
        self._schema = kw.get("schema", Schema)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ", ".join(repr(a) for a in self._args))

    def validate(self, data: str) -> str:
        """
        Validate data using defined sub schema/expressions ensuring all values are valid.
        :param data: Data to be validated with sub defined schemas.
        :return: Validated data
        """
        for s in [self._schema(s, error=self._error, ignore_extra_keys=self._ignore_extra_keys) for s in self._args]:
            data = s.validate(data)
        if os.path.isfile(data):
            return data
        else:
            raise Exception("{} isn't valid file.".format(data))


class Dir(object):
    """
    Wrapper class for Schema, adding support for directory exists validation.
    """

    def __init__(self, *args, **kw):
        self._args = args
        if not set(kw).issubset({"error", "schema", "ignore_extra_keys"}):
            diff = {"error", "schema", "ignore_extra_keys"}.difference(kw)
            raise TypeError("Unknown keyword arguments %r" % list(diff))
        self._error = kw.get("error")
        self._ignore_extra_keys = kw.get("ignore_extra_keys", False)
        self._schema = kw.get("schema", Schema)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ", ".join(repr(a) for a in self._args))

    def validate(self, data: str) -> str:
        """
        Validate data using defined sub schema/expressions ensuring all values are valid.
        :param data: Data to be validated with sub defined schemas.
        :return: Validated data
        """
        for s in [self._schema(s, error=self._error, ignore_extra_keys=self._ignore_extra_keys) for s in self._args]:
            data = s.validate(data)
        if os.path.isdir(data):
            return data
        else:
            raise Exception("{} isn't valid directory.".format(data))
