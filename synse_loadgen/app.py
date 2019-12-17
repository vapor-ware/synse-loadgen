"""Synse LoadGen application logic and request handlers."""

import asyncio
import functools
import random
import time
from typing import Union

import aiohttp
from asyncio_throttle import Throttler
from synse.client import HTTPClientV3, WebsocketClientV3

from synse_loadgen import cache, config
from synse_loadgen.log import logger, setup_logger

# Global cache to hold results from Synse Server
synse_cache = cache.AsyncCache()


async def err_invalid_endpoint(
        client: Union[HTTPClientV3, WebsocketClientV3],
        throttler: Throttler,
) -> None:
    """Handler to make a request against an endpoint which does not exist."""
    client_type = client.__class__.__name__

    if isinstance(client, HTTPClientV3):
        url = f'{client.url}/bad-route'
        try:
            async with throttler:
                _ = await client.make_request('GET', url)
        except Exception as e:
            # this is okay and what we expect
            logger.debug(
                'invalid endpoint request failed expectedly',
                url=url, err=e, client=client_type,
            )

    else:
        event = 'request/bad-event'
        try:
            async with throttler:
                _ = await client.request(event)
        except Exception as e:
            # this is okay and what we expect
            logger.debug(
                'invalid event request failed expectedly',
                request=event, err=e, client=client_type,
            )


def log_request(func):
    """Decorator to log information about the request being made."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        name = func.__name__[3:]
        client = args[0].__class__.__name__
        t = time.time()

        try:
            _ = await func(*args, **kwargs)

        except Exception as e:
            logger.exception(
                'failed request unexpectedly',
                request=name, client=client, err=e, t=time.time() - t,
            )
        else:
            logger.debug(
                'issued request',
                request=name, client=client, t=time.time() - t,
            )

    return wrapper


@log_request
async def on_status(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a status request."""
    if is_err:
        await err_invalid_endpoint(client, throttler)
    else:
        async with throttler:
            _ = await client.status()


@log_request
async def on_version(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a version request."""
    if is_err:
        await err_invalid_endpoint(client, throttler)
    else:
        async with throttler:
            _ = await client.version()


@log_request
async def on_scan(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a scan request."""
    if is_err:
        await err_invalid_endpoint(client, throttler)
    else:
        async with throttler:
            devices = await client.scan()
            ids = [d.id for d in devices]
            await synse_cache.set('devices', ids)

            # LEDs are collected separately so they can be used for writes
            leds = [d.id for d in devices if d.type.lower() == 'led']
            await synse_cache.set('leds', leds)


@log_request
async def on_read(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a read request."""
    if is_err:
        await err_invalid_endpoint(client, throttler)
    else:
        async with throttler:
            tags = random.choice([
                'system/type:temperature',
                ['system/type:pressure'],
                ['system/type:led', 'system/type:fan'],
                [['system/type:led'], ['system/type:humidity']],
            ])
            _ = await client.read(tags=tags)


@log_request
async def on_read_device(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a device read request."""
    if is_err:
        async with throttler:
            _ = await client.read_device('not-a-known-device-id')
    else:
        async with throttler:
            devs = await synse_cache.get('devices')
            if not devs:
                logger.debug(
                    'no devices cached, waiting for future scan request to rebuild device cache',
                )
                return

            _ = await client.read_device(random.choice(devs))


@log_request
async def on_plugin(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a plugin info request."""
    if is_err:
        async with throttler:
            _ = await client.plugin('not-a-known-plugin-id')
    else:
        async with throttler:
            plugins = await synse_cache.get('plugins')
            if not plugins:
                logger.debug(
                    'no plugins cached, waiting for future plugins request to rebuild plugins cache',
                )
                return

            _ = await client.plugin(random.choice(plugins))


@log_request
async def on_plugins(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing an enumerate plugins request."""
    if is_err:
        await err_invalid_endpoint(client, throttler)
    else:
        async with throttler:
            plugins = await client.plugins()
            ids = [p.id for p in plugins]
            await synse_cache.set('plugins', ids)


@log_request
async def on_plugin_health(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a plugin health request."""
    if is_err:
        await err_invalid_endpoint(client, throttler)
    else:
        async with throttler:
            _ = await client.plugin_health()


@log_request
async def on_tags(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a tags request."""
    if is_err:
        await err_invalid_endpoint(client, throttler)
    else:
        async with throttler:
            _ = await client.tags(
                ns=random.choice(['system', 'default', 'foobar', None]),
                ids=random.choice([True, False]),
            )


@log_request
async def on_info(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a device info request."""
    if is_err:
        async with throttler:
            _ = await client.info('not-a-known-device-id')
    else:
        async with throttler:
            devs = await synse_cache.get('devices')
            if not devs:
                logger.debug(
                    'no devices cached, waiting for future scan request to rebuild device cache',
                )
                return

            _ = await client.info(random.choice(devs))


@log_request
async def on_transaction(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a transaction info request."""
    if is_err:
        async with throttler:
            _ = await client.transaction('not-a-known-transaction-id')
    else:
        async with throttler:
            txns = await synse_cache.get('txns')
            if not txns:
                logger.debug(
                    'no transactions cached, waiting for future transactions request to rebuild cache',
                )
                return

            _ = await client.transaction(random.choice(txns))


@log_request
async def on_transactions(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing an enumerate transactions request."""
    if is_err:
        await err_invalid_endpoint(client, throttler)
    else:
        async with throttler:
            txns = await client.transactions()
            await synse_cache.set('txns', txns)


@log_request
async def on_write_async(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing an asynchronous write request."""
    if is_err:
        if random.randint(0, 1):
            # Issue a request to the correct device with the incorrect data.
            leds = await synse_cache.get('leds')
            # If there are no LEDs, this will fall back to the other failure request.
            if leds:
                async with throttler:
                    _ = await client.write_async(
                        device=random.choice(leds),
                        payload={'action': 'color', 'data': 'ff33aa'},
                    )
                return

        # Issue a request to a nonexistent device
        async with throttler:
            _ = await client.write_async(
                device='not-a-known-device-id',
                payload={'action': 'state', 'data': 'on'},
            )

    else:
        async with throttler:
            leds = await synse_cache.get('leds')
            if not leds:
                logger.debug(
                    'no LED devices cached, waiting for future scans request to rebuild cache',
                )
                return

            _ = await client.write_async(
                device=random.choice(leds),
                payload={'action': 'color', 'data': 'ff33aa'},
            )


@log_request
async def on_write_sync(
        client: Union[HTTPClientV3, WebsocketClientV3],
        is_err: bool,
        throttler: Throttler,
) -> None:
    """Handler for issuing a synchronous write request."""
    if is_err:
        if random.randint(0, 1):
            # Issue a request to the correct device with the incorrect data.
            leds = await synse_cache.get('leds')
            # If there are no LEDs, this will fall back to the other failure request.
            if leds:
                async with throttler:
                    _ = await client.write_sync(
                        device=random.choice(leds),
                        payload={'action': 'color', 'data': 'ff33aa'},
                    )
                return

        # Issue a request to a nonexistent device
        async with throttler:
            _ = await client.write_sync(
                device='not-a-known-device-id',
                payload={'action': 'state', 'data': 'on'},
            )

    else:
        async with throttler:
            leds = await synse_cache.get('leds')
            if not leds:
                logger.debug(
                    'no LED devices cached, waiting for future scans request to rebuild cache',
                )
                return

            _ = await client.write_sync(
                device=random.choice(leds),
                payload={'action': 'color', 'data': 'ff33aa'},
            )


async def run() -> None:
    """Run the Synse LoadGen application."""

    logger.info('starting application run')
    config.load_config()
    logger.info(
        'loaded configuration',
        config=config.options.config,
        source=config.options.config_file,
    )

    setup_logger()
    logger.info('configured logger')

    logger.debug('creating aiohttp client session')
    session = aiohttp.ClientSession(
        loop=asyncio.get_event_loop(),
        timeout=aiohttp.ClientTimeout(
            total=config.options.get('synse.timeout'),
        ),
    )

    # Note: setting the rate limit to something low can artificially inflate the latency
    # measurement around the time it takes for a request to complete because the timer
    # is above the context of the throttler, so any time spent waiting by the throttler is
    # counted in the latency measurement which is not correct.
    throttler = Throttler(rate_limit=config.options.get('settings.rate'))

    async with session as s:
        logger.debug('creating Synse HTTP client')
        httpv3 = HTTPClientV3(
            host=config.options.get('synse.host'),
            port=config.options.get('synse.port'),
            timeout=config.options.get('synse.timeout'),
            session=s,
        )

        logger.debug('creating Synse WebSocket client')
        wsv3 = WebsocketClientV3(
            host=config.options.get('synse.host'),
            port=config.options.get('synse.port'),
            session=s,
        )
        logger.debug('connecting WebSocket')
        await wsv3.connect()

        requests = [
            'status',
            'version',
            'scan',
            'read',
            'read_device',
            'write_sync',
            'write_async',
            'transaction',
            'transactions',
            'plugin',
            'plugins',
            'plugin_health',
            'tags',
            'info',
        ]

        err_ratio = config.options.get('settings.error_ratio')
        while True:
            await globals().get(f'on_{random.choice(requests)}')(
                random.choice((httpv3, wsv3)),
                random.random() <= err_ratio,
                throttler,
            )
            await asyncio.sleep(0.05)
