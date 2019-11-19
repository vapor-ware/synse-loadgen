# Synse LoadGen

`synse-loadgen` is a service which generates requests against the Synse Server API.
It is intended to be used for testing and development, providing a means by which to
exercise the API and ensure that:
- It can handle some load of requests
- It succeeds and fails in an expected manner
- Synse Server remains stable and performant over time under load
- No bugs slipped through the cracks

## Usage

You can get the image from DockerHub

```
docker pull vaporio/synse-loadgen
```

A basic example deployment has been included in [docker-compose.yaml](docker-compose.yaml).
This can be run with:

```
docker-compose up -d
```

Once running, you can look at the `synse-loadgen` logs or `synse-server` logs and see
that requests are being made.

## Configuring

| Field | Description | Default |
| :---- | :---------- | ------- |
| `logging` | Set the logging level for the application. | `debug` |
| `synse.host` | The hostname/IP address of the Synse Server instance to connect to. | - |
| `synse.port` | The exposed port of the Synse Server instance to connect to. | `5000` |
| `synse.timeout` | The timeout (in seconds) for a request to resolve. | `5` |
| `settings.rate` | The rate (requests/second) to issue requests against the Synse API. | `5` |
| `settings.error_ratio` | The ratio of requests which should be sent in error. This value should be between 0 and 1. Requests in error include bad data, bad query params, invalid URLs, etc. | `0.02` |

