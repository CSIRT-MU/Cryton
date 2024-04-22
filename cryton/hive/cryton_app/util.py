from datetime import datetime
import yaml
import configparser
import json
import pytz
from jinja2 import nativetypes, DebugUndefined, ChainableUndefined, UndefinedError
from abc import ABC, abstractmethod

from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from django.db.models.query import QuerySet
from django.db.models import ObjectDoesNotExist
from django.db import IntegrityError, DatabaseError
from django.utils.datastructures import MultiValueDict

from cryton.hive.cryton_app import exceptions, serializers
from cryton.hive.utility import util as core_util, constants, exceptions as core_exceptions


def filter_decorator(func):
    """
    Decorator for filtering of serializer results.
    :param func:
    :return: Filtered queryset
    """

    def inner(self):
        """
        Filter queryset using request's params.
        :param self:
        :return: Filtered queryset
        """
        # Create dictionary filter from request
        filters_dict = {key: value for key, value in self.request.query_params.items()}

        # Get rid of parameters that would get in a way of filter
        order_by_param = filters_dict.pop("order_by", "id")
        filters_dict.pop("limit", None)
        filters_dict.pop("offset", None)

        # Obtain queryset
        queryset: QuerySet = func(self)

        # Update filters (optionally with __icontains)
        unsearchable_keys = [
            "run_id",
            "plan_execution_id",
            "stage_execution_id",
            "step_execution_id",
            "plan_model_id",
            "stage_model_id",
            "step_model_id",
        ]
        filters_dict_update = {}

        for key, value in filters_dict.items():
            if key not in unsearchable_keys:
                filters_dict_update.update({key + "__icontains": value})
            else:
                filters_dict_update.update({key: value})

        # Filter and order queryset
        queryset = queryset.filter(**filters_dict_update)
        queryset = queryset.order_by(order_by_param)

        return queryset

    return inner


def get_start_time(request_data: dict) -> datetime:
    """
    Parse start time and its timezone.
    :param request_data: Incoming request data
    :return: Normalized start time
    """
    time_zone = request_data.get("time_zone", "utc")
    try:
        str_start_time = request_data["start_time"]
    except KeyError:
        raise exceptions.ValidationError("'start_time' parameter unfilled!")

    try:
        start_time = datetime.strptime(str_start_time, constants.TIME_FORMAT)
    except ValueError:
        try:
            start_time = datetime.strptime(str_start_time, constants.TIME_FORMAT_DETAILED)
        except ValueError:
            raise exceptions.ValidationError(
                f"'start_time' parameter must be in '{constants.TIME_FORMAT}' or "
                f"'{constants.TIME_FORMAT_DETAILED}' format!"
            )

    try:
        start_time = core_util.convert_to_utc(start_time, time_zone)
    except pytz.UnknownTimeZoneError:
        raise exceptions.ValidationError("Defined 'time_zone' is not supported!")

    return start_time


def parse_inventory(inventory: str) -> dict:
    """
    Reads inventory file (JSON, YAML, INI) and returns it as a dictionary
    :param inventory: Inventory file content
    :return: Inventory variables
    """
    # JSON
    try:
        return json.loads(inventory)
    except json.decoder.JSONDecodeError:
        pass

    # YAML
    try:
        return yaml.safe_load(inventory)
    except yaml.YAMLError:
        pass

    # INI
    try:
        config_parser = configparser.ConfigParser()
        config_parser.read_string(inventory)
        return {section: dict(config_parser.items(section)) for section in config_parser.sections()}
    except configparser.Error:
        pass

    raise ValueError(f"Inventory file must contain data and be of type JSON, YAML, or INI. File: {inventory}")


def get_inventory_variables_from_files(files: MultiValueDict) -> dict:
    """
    Get all inventory variables from input.
    :param files: Files to parse
    :return: All inventory variables
    """
    # Get inventory files from request and load them
    inventory_variables = {}
    for inventory_file in files.values():
        file_content = inventory_file.read()
        if isinstance(file_content, bytes):
            file_content = file_content.decode("utf-8")

        try:
            inventory_variables.update(parse_inventory(file_content))
        except ValueError as ex:
            raise exceptions.ValidationError(
                f"Cannot read inventory file. Original exception: {ex}. " f"Inventory file: {inventory_file}."
            )

    return inventory_variables


class IgnoreNestedUndefined(ChainableUndefined, DebugUndefined):
    def __getattr__(self, attr: str) -> "IgnoreNestedUndefined":
        self._undefined_name += f".{attr}"

        return self

    def __getitem__(self, item: str) -> "IgnoreNestedUndefined":
        self._undefined_name += f"[{item}]"

        return self


def fill_template(inventory_variables: dict, template: str) -> str:
    """
    Fill Jinja variables in the template (if there are any inventory variables).
    :param inventory_variables: Template variables to fill the template with
    :param template: Template to fill
    :return: Filled template
    """
    # Either fill the Plan template or consider the template already filled
    if inventory_variables == {}:
        return template

    env = nativetypes.NativeEnvironment(undefined=IgnoreNestedUndefined)

    try:
        plan_template_obj = env.from_string(template)
        return plan_template_obj.render(**inventory_variables)
    except (TypeError, UndefinedError) as ex:
        raise exceptions.ValidationError(f"File is not a valid Jinja template, original exception: {ex}")


def parse_object_from_files(files: MultiValueDict) -> dict:
    """
    Get serialized object from input - parse template and fill it with inventory variables.
    :param files: Input files
    :return: Serialized object
    """
    try:
        uploaded_template = files.pop("file")[0].read().decode()
    except Exception:
        raise exceptions.ValidationError("Parameter `file` has invalid content and couldn't be read.")

    inventory_variables = get_inventory_variables_from_files(files)
    filled_template = fill_template(inventory_variables, uploaded_template)

    try:
        return yaml.safe_load(filled_template)
    except (ValueError, yaml.YAMLError) as ex:
        raise exceptions.ValidationError(f"Cannot read file. Original exception: {ex}. File: {filled_template}.")


class BaseViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    A ViewSet that provides default list() action.
    """


class InstanceViewSet(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, BaseViewSet, ABC):
    """
    A ViewSet that provides default retrieve(), destroy(), and list() actions.
    """

    @filter_decorator
    def get_queryset(self):
        queryset = self.queryset

        return queryset

    @extend_schema(
        description="Delete an object with given id.",
        responses={
            204: serializers.BaseSerializer,
            404: serializers.DetailStringSerializer,
        },
    )
    def destroy(self, _, *args, **kwargs):
        model_id = kwargs.get("pk")
        try:
            self._destroy(model_id)
        except (ObjectDoesNotExist, core_exceptions.ObjectDoesNotExist):
            raise exceptions.NotFound()
        except IntegrityError:
            raise exceptions.ValidationError("Unable to delete as the entry is referenced from another.")
        except DatabaseError as ex:
            raise exceptions.ValidationError(f"Unable to delete. Reason: {type(ex)}")

        return Response(status=status.HTTP_204_NO_CONTENT)

    @abstractmethod
    def _destroy(self, model_id: int):
        """
        Override this method to delete the correct object.
        :param model_id: ID of the desired object
        :return: None
        """
        pass


class InstanceFullViewSet(mixins.CreateModelMixin, InstanceViewSet, ABC):
    """
    A ViewSet that provides default retrieve(), destroy(), list(), and create() actions.
    """


class ExecutionViewSet(InstanceViewSet, ABC):
    """
    A ViewSet that provides default retrieve(), destroy(), and list() actions.
    """


class ExecutionFullViewSet(InstanceFullViewSet, ABC):
    """
    A ViewSet that provides default retrieve(), destroy(), list(), and create() actions.
    """
