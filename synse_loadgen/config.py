"""Synse LoadGen configuration and scheme definition."""

from bison import Bison, DictOption, Option, Scheme

from synse_loadgen.log import logger

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


def load_config() -> None:
    """Load application configuration from YAML file, if it exists."""
    logger.info('loading application configuration')
    options.add_config_paths(
        '.',
        '/etc/synse-loadgen',
    )

    options.env_prefix = 'SLG'
    options.auto_env = True

    options.parse(requires_cfg=False)
    options.validate()
