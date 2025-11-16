"""Test progress tracking functionality."""

from typing import Any

from dotfiles_pipeline import Pipeline, PipelineContext, PipelineStep


class SimpleStep(PipelineStep):
    """Simple test step."""

    def __init__(self, step_id: str, result_value: str):
        """Initialize simple step."""
        self._step_id = step_id
        self._result_value = result_value

    @property
    def step_id(self) -> str:
        """Return step ID."""
        return self._step_id

    @property
    def description(self) -> str:
        """Return step description."""
        return f"Simple step: {self._step_id}"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        """Add result to context."""
        context.results[self._step_id] = self._result_value
        return context


def test_progress_callback():
    """Test that progress callback is called correctly."""
    progress_updates = []

    def callback(step_index, total_steps, step_name, progress):
        progress_updates.append(
            {
                "step_index": step_index,
                "total_steps": total_steps,
                "step_name": step_name,
                "progress": progress,
            }
        )

    steps = [
        SimpleStep("step1", "done1"),
        SimpleStep("step2", "done2"),
        SimpleStep("step3", "done3"),
    ]

    # Create a minimal context
    class MockLogger:
        def info(self, msg):
            pass

        def error(self, msg):
            pass

    class MockConfig:
        pass

    context = PipelineContext(
        app_config=MockConfig(), logger_instance=MockLogger()
    )

    pipeline = Pipeline(steps=steps, progress_callback=callback)
    result = pipeline.run(context)

    # Verify callback was called 3 times
    assert len(progress_updates) == 3

    # Verify first update
    assert progress_updates[0]["step_index"] == 0
    assert progress_updates[0]["total_steps"] == 3
    assert progress_updates[0]["step_name"] == "step1"
    assert abs(progress_updates[0]["progress"] - 33.333333333333336) < 0.01

    # Verify second update
    assert progress_updates[1]["step_index"] == 1
    assert progress_updates[1]["total_steps"] == 3
    assert progress_updates[1]["step_name"] == "step2"
    assert abs(progress_updates[1]["progress"] - 66.666666666666671) < 0.01

    # Verify third update
    assert progress_updates[2]["step_index"] == 2
    assert progress_updates[2]["total_steps"] == 3
    assert progress_updates[2]["step_name"] == "step3"
    assert progress_updates[2]["progress"] == 100.0

    # Verify results were added to context
    assert result.results["step1"] == "done1"
    assert result.results["step2"] == "done2"
    assert result.results["step3"] == "done3"

    print("✓ Progress callback test passed")


def test_status_methods():
    """Test status query methods."""
    steps = [
        SimpleStep("step1", "done1"),
        SimpleStep("step2", "done2"),
    ]

    class MockLogger:
        def info(self, msg):
            pass

        def error(self, msg):
            pass

    class MockConfig:
        pass

    context = PipelineContext(
        app_config=MockConfig(), logger_instance=MockLogger()
    )

    pipeline = Pipeline(steps=steps)

    # Before execution
    assert pipeline.is_running() is False
    assert pipeline.get_current_step() is None
    status = pipeline.get_status()
    assert status["progress"] == 0.0
    assert status["current_step"] is None
    assert status["is_running"] is False

    # Execute
    pipeline.run(context)

    # After execution
    assert pipeline.is_running() is False
    assert pipeline.get_current_step() is None

    print("✓ Status methods test passed")


if __name__ == "__main__":
    test_progress_callback()
    test_status_methods()
    print("\n✅ All tests passed!")
