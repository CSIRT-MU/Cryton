#!/bin/sh

cryton-hive migrate || exit 1
exec "$@"
