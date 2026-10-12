# process-bigraph-lang

[![Release](https://img.shields.io/github/v/release/biosimulations/process-bigraph-lang)](https://img.shields.io/github/v/release/biosimulations/process-bigraph-lang)
[![Build status](https://img.shields.io/github/actions/workflow/status/biosimulations/process-bigraph-lang/main.yml?branch=main)](https://github.com/biosimulations/process-bigraph-lang/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/biosimulations/process-bigraph-lang/branch/main/graph/badge.svg)](https://codecov.io/gh/biosimulations/process-bigraph-lang)
[![Commit activity](https://img.shields.io/github/commit-activity/m/biosimulations/process-bigraph-lang)](https://img.shields.io/github/commit-activity/m/biosimulations/process-bigraph-lang)
[![License](https://img.shields.io/github/license/biosimulations/process-bigraph-lang)](https://img.shields.io/github/license/biosimulations/process-bigraph-lang)

A language server, CLI and Python package for `.pblang`, a domain specific language that describes
[process bigraph](https://github.com/vivarium-collective/process-bigraph) composites: a tree-shaped, verifiable
projection of the composite document, with imported interface declarations, parameters, open sites, units and
model headers that the checker verifies before anything runs. See [the architecture](docs/architecture.md) and
[the design](docs/v2/design.md).

```bash
pip install process_bigraph_lang
python -m process_bigraph_lang.v2 compile composite.pblang --interfaces headers.manifest.json -o composite.json
python -m process_bigraph_lang.v2 decompile composite.json
python -m process_bigraph_lang.v2 check composite.pblang --interfaces headers.manifest.json
python -m process_bigraph_lang.v2 describe my_package.processes --manifest headers.manifest.json --out headers/
```

- **Github repository**: <https://github.com/biosimulations/process-bigraph-lang/>
- **Documentation** <https://biosimulations.github.io/process-bigraph-lang/>

## Getting started with your project

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:biosimulations/process-bigraph-lang.git
git push -u origin main
```

Finally, install the environment and the pre-commit hooks with

```bash
make install
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPI or Artifactory, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).

## Releasing a new version

- Create an API Token on [PyPI](https://pypi.org/).
- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting [this page](https://github.com/biosimulations/process-bigraph-lang/settings/secrets/actions/new).
- Create a [new release](https://github.com/biosimulations/process-bigraph-lang/releases/new) on Github.
- Create a new tag in the form `*.*.*`.
- For more details, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/cicd/#how-to-trigger-a-release).

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
