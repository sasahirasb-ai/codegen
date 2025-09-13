import os

import nox


@nox.session(venv_backend="uv", python=["3.12"], tags=["test"])
def test(session):
    session.run("uv", "sync", "--dev")
    session.env["PYTHONPATH"] = os.path.abspath(".")
    session.run("uv", "run", "--dev", "pytest")


@nox.session(venv_backend="uv", python=["3.12"], tags=["coverage"])
def test_coverage(session):
    session.run("uv", "sync", "--dev")
    session.env["PYTHONPATH"] = os.path.abspath(".")
    session.run(
        "uv", "run", "--dev", "pytest", "--cov=src", "--cov-report=json:coverage.json"
    )
