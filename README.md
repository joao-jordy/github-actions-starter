# GitHub Actions starter

This repository currently provides a **CI foundation**, not the requested
production CI/CD platform. It does not create AWS resources or deploy software.
Do not treat a passing CI run as a deployment, security, or compliance gate.

## What works

`ci.yml` runs for pull requests, pushes to `main`, and manual dispatches. It
calls `config.yml`, which validates the repository or organization `SERVICES`
variable and uses `dorny/paths-filter` to select services whose paths changed.
Changes to `.github/` or the configuration script select every service; manual
dispatch also selects every service. Each selected service must provide a
`Makefile` with a `ci` target. That target is responsible for running the
service's checks and returning a nonzero exit code on failure. The matrix runs
services in parallel; the runner uses its preinstalled tools.

```text
pull request / main push / manual
               |
        resolve and validate
               |
        changed-path filter
               |
     make ci for each selected service
```

Set the repository variable `SERVICES` to a nonempty JSON array, for example:

```json
[
  {"name":"web","path":"apps/web","type":"static","language":"typescript"},
  {"name":"hello-go","path":"apps/hello-go","type":"lambda","language":"go","runtime":"provided.al2023"}
]
```

Names and paths must be unique. Names use lowercase letters, digits and hyphens,
starting with a letter; `pipeline` is reserved. Paths are relative, contain no
glob characters or traversal components, and point to service directories.
Supported types are `static`, `lambda`, and `container`; supported languages
are `go`, `rust`, `python`, `typescript`, `javascript`, `java`, and `dotnet`.
Other fields are carried through to the matrix. Missing, empty or invalid
configuration fails the workflow. No sample applications are included.

## Minimal configuration per combination

Every service needs `name`, `path`, `type` and `language`. Any combination of
the values below is valid; replace `name` and `path` with your own unique values.
Extra fields (such as `runtime`) are passed through to the matrix and are optional.

### `static` — static site or assets

| Language | Minimal entry |
| --- | --- |
| `go` | `{"name":"go-static","path":"apps/go-static","type":"static","language":"go"}` |
| `rust` | `{"name":"rust-static","path":"apps/rust-static","type":"static","language":"rust"}` |
| `python` | `{"name":"python-static","path":"apps/python-static","type":"static","language":"python"}` |
| `typescript` | `{"name":"typescript-static","path":"apps/typescript-static","type":"static","language":"typescript"}` |
| `javascript` | `{"name":"javascript-static","path":"apps/javascript-static","type":"static","language":"javascript"}` |
| `java` | `{"name":"java-static","path":"apps/java-static","type":"static","language":"java"}` |
| `dotnet` | `{"name":"dotnet-static","path":"apps/dotnet-static","type":"static","language":"dotnet"}` |

### `lambda` — serverless function (add `runtime`, e.g. `provided.al2023`)

| Language | Minimal entry |
| --- | --- |
| `go` | `{"name":"go-lambda","path":"apps/go-lambda","type":"lambda","language":"go"}` |
| `rust` | `{"name":"rust-lambda","path":"apps/rust-lambda","type":"lambda","language":"rust"}` |
| `python` | `{"name":"python-lambda","path":"apps/python-lambda","type":"lambda","language":"python"}` |
| `typescript` | `{"name":"typescript-lambda","path":"apps/typescript-lambda","type":"lambda","language":"typescript"}` |
| `javascript` | `{"name":"javascript-lambda","path":"apps/javascript-lambda","type":"lambda","language":"javascript"}` |
| `java` | `{"name":"java-lambda","path":"apps/java-lambda","type":"lambda","language":"java"}` |
| `dotnet` | `{"name":"dotnet-lambda","path":"apps/dotnet-lambda","type":"lambda","language":"dotnet"}` |

### `container` — container image service

| Language | Minimal entry |
| --- | --- |
| `go` | `{"name":"go-container","path":"apps/go-container","type":"container","language":"go"}` |
| `rust` | `{"name":"rust-container","path":"apps/rust-container","type":"container","language":"rust"}` |
| `python` | `{"name":"python-container","path":"apps/python-container","type":"container","language":"python"}` |
| `typescript` | `{"name":"typescript-container","path":"apps/typescript-container","type":"container","language":"typescript"}` |
| `javascript` | `{"name":"javascript-container","path":"apps/javascript-container","type":"container","language":"javascript"}` |
| `java` | `{"name":"java-container","path":"apps/java-container","type":"container","language":"java"}` |
| `dotnet` | `{"name":"dotnet-container","path":"apps/dotnet-container","type":"container","language":"dotnet"}` |

Each service directory must contain a `Makefile` with a `ci` target, for example:

```make
ci:
	@echo "run lint, tests and build here"
```

Run the configuration tests locally with:

```sh
python3 -m unittest discover -s tests -v
```

## Not implemented

The requested Terraform bootstrap, environment provisioning and protection
configuration, sample applications, language-specific composite actions,
integration and security stages, artifact publication, signing, deployment,
promotion, rollback, notifications, and scheduled jobs are **not implemented**.
There are no AWS roles, state buckets, IAM policies, or deployment approvals in
this repository. These must be designed, implemented, and independently
validated before the pipeline can be used to deploy anything.
