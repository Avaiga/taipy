from unittest.mock import Mock, patch

import pytest

from src.taipy.gui_core._context import _GuiCoreContext, _SubmissionStatus
from taipy import Status


class MockJob:
    def __init__(self, id: str, status):
        self.status = status
        self.id = id

    def is_failed(self):
        return self.status == Status.FAILED

    def is_canceled(self):
        return self.status == Status.CANCELED

    def is_blocked(self):
        return self.status == Status.BLOCKED

    def is_pending(self):
        return self.status == Status.PENDING

    def is_running(self):
        return self.status == Status.RUNNING

    def is_completed(self):
        return self.status == Status.COMPLETED

    def is_skipped(self):
        return self.status == Status.SKIPPED

    def is_abandoned(self):
        return self.status == Status.ABANDONED

    def is_submitted(self):
        return self.status == Status.SUBMITTED


def mock_core_get(entity_id):
    jobs = {
        "job0_submitted": MockJob("job0_submitted", Status.SUBMITTED),
        "job1_failed": MockJob("job1_failed", Status.FAILED),
        "job2_canceled": MockJob("job2_canceled", Status.CANCELED),
        "job3_blocked": MockJob("job3_blocked", Status.BLOCKED),
        "job4_pending": MockJob("job4_pending", Status.PENDING),
        "job5_running": MockJob("job5_running", Status.RUNNING),
        "job6_completed": MockJob("job6_completed", Status.COMPLETED),
        "job7_skipped": MockJob("job7_skipped", Status.SKIPPED),
        "job8_abandoned": MockJob("job8_abandoned", Status.ABANDONED),
    }
    return jobs[entity_id]


class TestGuiCoreContext_SubmissionStatus:
    @pytest.mark.parametrize(
        "job_ids, expected_status",
        [
            (["job1_failed"], _SubmissionStatus.FAILED),
            (["job2_canceled"], _SubmissionStatus.CANCELED),
            (["job3_blocked"], _SubmissionStatus.BLOCKED),
            (["job4_pending"], _SubmissionStatus.WAITING),
            (["job5_running"], _SubmissionStatus.RUNNING),
            (["job6_completed"], _SubmissionStatus.COMPLETED),
            (["job7_skipped"], _SubmissionStatus.COMPLETED),
            (["job8_abandoned"], _SubmissionStatus.UNDEFINED),
        ],
    )
    def test_single_job(self, job_ids, expected_status):
        with patch("src.taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            status = gui_core_context._get_submittable_status(job_ids)
            assert status == expected_status

    @pytest.mark.parametrize(
        "job_ids, expected_status",
        [
            (["job1_failed", "job1_failed"], _SubmissionStatus.FAILED),
            (["job1_failed", "job2_canceled"], _SubmissionStatus.FAILED),
            (["job1_failed", "job3_blocked"], _SubmissionStatus.FAILED),
            (["job1_failed", "job4_pending"], _SubmissionStatus.FAILED),
            (["job1_failed", "job5_running"], _SubmissionStatus.FAILED),
            (["job1_failed", "job6_completed"], _SubmissionStatus.FAILED),
            (["job1_failed", "job7_skipped"], _SubmissionStatus.FAILED),
            (["job1_failed", "job8_abandoned"], _SubmissionStatus.FAILED),
            (["job2_canceled", "job1_failed"], _SubmissionStatus.FAILED),
            (["job3_blocked", "job1_failed"], _SubmissionStatus.FAILED),
            (["job4_pending", "job1_failed"], _SubmissionStatus.FAILED),
            (["job5_running", "job1_failed"], _SubmissionStatus.FAILED),
            (["job6_completed", "job1_failed"], _SubmissionStatus.FAILED),
            (["job7_skipped", "job1_failed"], _SubmissionStatus.FAILED),
            (["job8_abandoned", "job1_failed"], _SubmissionStatus.FAILED),
        ],
    )
    def test_one_failed_job(self, job_ids, expected_status):
        with patch("src.taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            status = gui_core_context._get_submittable_status(job_ids)
            assert status == expected_status

    @pytest.mark.parametrize(
        "job_ids, expected_status",
        [
            (["job2_canceled", "job2_canceled"], _SubmissionStatus.CANCELED),
            (["job2_canceled", "job3_blocked"], _SubmissionStatus.CANCELED),
            (["job2_canceled", "job4_pending"], _SubmissionStatus.CANCELED),
            (["job2_canceled", "job5_running"], _SubmissionStatus.CANCELED),
            (["job2_canceled", "job6_completed"], _SubmissionStatus.CANCELED),
            (["job2_canceled", "job7_skipped"], _SubmissionStatus.CANCELED),
            (["job2_canceled", "job8_abandoned"], _SubmissionStatus.CANCELED),
            (["job3_blocked", "job2_canceled"], _SubmissionStatus.CANCELED),
            (["job4_pending", "job2_canceled"], _SubmissionStatus.CANCELED),
            (["job5_running", "job2_canceled"], _SubmissionStatus.CANCELED),
            (["job6_completed", "job2_canceled"], _SubmissionStatus.CANCELED),
            (["job7_skipped", "job2_canceled"], _SubmissionStatus.CANCELED),
            (["job8_abandoned", "job2_canceled"], _SubmissionStatus.CANCELED),
        ],
    )
    def test_no_failed_one_cancel(self, job_ids, expected_status):
        with patch("src.taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            status = gui_core_context._get_submittable_status(job_ids)
            assert status == expected_status

    @pytest.mark.parametrize(
        "job_ids, expected_status",
        [
            (["job4_pending", "job3_blocked"], _SubmissionStatus.WAITING),
            (["job4_pending", "job4_pending"], _SubmissionStatus.WAITING),
            (["job4_pending", "job6_completed"], _SubmissionStatus.WAITING),
            (["job4_pending", "job7_skipped"], _SubmissionStatus.WAITING),
            (["job3_blocked", "job4_pending"], _SubmissionStatus.WAITING),
            (["job6_completed", "job4_pending"], _SubmissionStatus.WAITING),
            (["job7_skipped", "job4_pending"], _SubmissionStatus.WAITING),
        ],
    )
    def test_no_failed_or_cancel_one_pending(self, job_ids, expected_status):
        with patch("src.taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            status = gui_core_context._get_submittable_status(job_ids)
            assert status == expected_status

    @pytest.mark.parametrize(
        "job_ids, expected_status",
        [
            (["job5_running", "job3_blocked"], _SubmissionStatus.RUNNING),
            (["job5_running", "job4_pending"], _SubmissionStatus.RUNNING),
            (["job5_running", "job5_running"], _SubmissionStatus.RUNNING),
            (["job5_running", "job6_completed"], _SubmissionStatus.RUNNING),
            (["job5_running", "job7_skipped"], _SubmissionStatus.RUNNING),
            (["job3_blocked", "job5_running"], _SubmissionStatus.RUNNING),
            (["job4_pending", "job5_running"], _SubmissionStatus.RUNNING),
            (["job6_completed", "job5_running"], _SubmissionStatus.RUNNING),
            (["job7_skipped", "job5_running"], _SubmissionStatus.RUNNING),
        ],
    )
    def test_no_failed_cancel_nor_pending_one_running(self, job_ids, expected_status):
        with patch("src.taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            status = gui_core_context._get_submittable_status(job_ids)
            assert status == expected_status

    @pytest.mark.parametrize(
        "job_ids, expected_status",
        [
            (["job3_blocked", "job3_blocked"], _SubmissionStatus.BLOCKED),
            (["job3_blocked", "job6_completed"], _SubmissionStatus.BLOCKED),
            (["job3_blocked", "job7_skipped"], _SubmissionStatus.BLOCKED),
            (["job6_completed", "job3_blocked"], _SubmissionStatus.BLOCKED),
            (["job7_skipped", "job3_blocked"], _SubmissionStatus.BLOCKED),
        ],
    )
    def test_no_failed_cancel_pending_nor_running_one_blocked(self, job_ids, expected_status):
        with patch("src.taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            status = gui_core_context._get_submittable_status(job_ids)
            assert status == expected_status

    @pytest.mark.parametrize(
        "job_ids, expected_status",
        [
            (["job6_completed", "job6_completed"], _SubmissionStatus.COMPLETED),
            (["job6_completed", "job7_skipped"], _SubmissionStatus.COMPLETED),
            (["job7_skipped", "job6_completed"], _SubmissionStatus.COMPLETED),
            (["job7_skipped", "job7_skipped"], _SubmissionStatus.COMPLETED),
        ],
    )
    def test_only_completed_or_skipped(self, job_ids, expected_status):
        with patch("src.taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            status = gui_core_context._get_submittable_status(job_ids)
            assert status == expected_status

    @pytest.mark.parametrize(
        "job_ids, expected_status",
        [
            (["job3_blocked", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job4_pending", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job5_running", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job6_completed", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job7_skipped", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job3_blocked"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job4_pending"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job5_running"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job6_completed"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job7_skipped"], _SubmissionStatus.UNDEFINED),
        ],
    )
    def test_WRONG_CASE_abandoned_without_cancel_or_failed(self, job_ids, expected_status):
        with patch("src.taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            status = gui_core_context._get_submittable_status(job_ids)
            assert status == expected_status

    @pytest.mark.parametrize(
        "job_ids, expected_status",
        [
            (["job3_blocked", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job4_pending", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job5_running", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job6_completed", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job7_skipped", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job8_abandoned"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job3_blocked"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job4_pending"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job5_running"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job6_completed"], _SubmissionStatus.UNDEFINED),
            (["job8_abandoned", "job7_skipped"], _SubmissionStatus.UNDEFINED),
        ],
    )
    def test_WRONG_CASE_abandoned_without_cancel_or_failed(self, job_ids, expected_status):
        with patch("src.taipy.gui_core._context.core_get", side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            status = gui_core_context._get_submittable_status(job_ids)
            assert status == expected_status

    def test_no_job(self):
        with patch('src.taipy.gui_core._context.core_get', side_effect=mock_core_get):
            gui_core_context = _GuiCoreContext(Mock())
            status = gui_core_context._get_submittable_status([])
            assert status == _SubmissionStatus.UNDEFINED

