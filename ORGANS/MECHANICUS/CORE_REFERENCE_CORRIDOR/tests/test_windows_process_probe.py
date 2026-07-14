"""Regression proof for Windows process liveness under Python UTF-8 mode."""

from __future__ import annotations

import os
import subprocess

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR import negative_observer


pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows-only tasklist probe")


def test_tasklist_probe_treats_localized_output_as_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: dict[str, object] = {}

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        observed["argv"] = argv
        observed["kwargs"] = kwargs
        return subprocess.CompletedProcess(
            argv,
            0,
            stdout=b"\x88\xac\xef \xae\xa1\xe0\xa0\xa7\xa0,\"4242\"\r\n",
            stderr=b"",
        )

    monkeypatch.setattr(negative_observer.subprocess, "run", fake_run)

    assert negative_observer._process_alive(4242) is True
    kwargs = observed["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["text"] is False
    assert kwargs["stdout"] is subprocess.PIPE
    assert kwargs["stderr"] is subprocess.PIPE


def test_tasklist_probe_rejects_nonmatching_pid(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(argv, 0, stdout=b'"python.exe","9999"\r\n', stderr=b"")

    monkeypatch.setattr(negative_observer.subprocess, "run", fake_run)

    assert negative_observer._process_alive(4242) is False
