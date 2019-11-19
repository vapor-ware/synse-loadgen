"""Synse LoadGen configuration and scheme definition."""

from bison import Bison, DictOption, Option, Scheme

# The Synse LoadGen configuration scheme
scheme = Scheme(
    Option('logging', default='debug', choices=['debug', 'info', 'warning', 'error', 'critical']),
    DictOption('synse', default={}, scheme=Scheme(
        Option('host', required=True, field_type=str, bind_env=True),
        Option('port', default=5000, field_type=int, bind_env=True),
        Option('timeout', default=5, field_type=int, bind_env=True),
    )),
    DictOption('settings', default={}, scheme=Scheme(
        Option('rate', default=5, field_type=int, bind_env=True),
        Option('error_ratio', default=0.02, field_type=float, bind_env=True),
    )),
)

# Configuration options manager for Synse LoadGen. All access to configuration
# data should be done through `options`.
options = Bison(scheme)
