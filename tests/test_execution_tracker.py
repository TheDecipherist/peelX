#!/usr/bin/env python3
"""Test ExecutionTracker persistence and tracking."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import shutil
import json
from interactive_selector import ExecutionTracker


@pytest.fixture
def temp_dir():
    d = Path(tempfile.mkdtemp(prefix="tracker_test_"))
    yield d
    shutil.rmtree(d)


class TestExecutionTracker:
    """Tests for ExecutionTracker persistence and counting."""

    def test_initial_state_empty(self, temp_dir: Path):
        tracker = ExecutionTracker(log_file=temp_dir / "test.log")
        assert tracker.get_execution_count("/fake/path") == 0
        assert tracker.has_been_run("/fake/path") is False

    def test_record_execution(self, temp_dir: Path):
        tracker = ExecutionTracker(log_file=temp_dir / "test.log")
        tracker.record_execution("/some/exe")
        assert tracker.get_execution_count("/some/exe") == 1
        assert tracker.has_been_run("/some/exe") is True

    def test_multiple_executions_increment(self, temp_dir: Path):
        tracker = ExecutionTracker(log_file=temp_dir / "test.log")
        tracker.record_execution("/some/exe")
        tracker.record_execution("/some/exe")
        tracker.record_execution("/some/exe")
        assert tracker.get_execution_count("/some/exe") == 3

    def test_persistence_across_instances(self, temp_dir: Path):
        log_file = temp_dir / "test.log"
        tracker1 = ExecutionTracker(log_file=log_file)
        tracker1.record_execution("/some/exe")

        tracker2 = ExecutionTracker(log_file=log_file)
        assert tracker2.get_execution_count("/some/exe") == 1
        assert tracker2.has_been_run("/some/exe") is True

    def test_timestamps_recorded(self, temp_dir: Path):
        log_file = temp_dir / "test.log"
        tracker = ExecutionTracker(log_file=log_file)
        tracker.record_execution("/some/exe")

        data = json.loads(log_file.read_text())
        entry = data["/some/exe"]
        assert entry["first_run"] is not None
        assert entry["last_run"] is not None

    def test_corrupt_log_handled(self, temp_dir: Path):
        log_file = temp_dir / "test.log"
        log_file.write_text("not valid json")

        tracker = ExecutionTracker(log_file=log_file)
        assert tracker.get_execution_count("/any") == 0
