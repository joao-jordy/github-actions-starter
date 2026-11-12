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
