"""Main pipeline interface following the Log class pattern."""

from .core.types import (
    PipelineConfig,
    PipelineContext,
    TaskStep,
)
from .executors.pipeline_executor import PipelineExecutor


class Pipeline:
    """
    Main pipeline interface for step execution.

    Provides a clean, high-level API for executing steps in serial and parallel,
    similar to the Log class pattern used in the logging module.
    """

    def __init__(
        self, steps: list[TaskStep], config: PipelineConfig | None = None
    ):
        """
        Initialize pipeline with steps and configuration.

        Args:
            steps: List of pipeline steps (steps or parallel groups)
            config: Pipeline configuration (optional)

        Examples:
            # Serial execution
            pipeline = Pipeline([step1, step2, step3])

            # Parallel groups
            pipeline = Pipeline([
                [step1, step2, step3],  # parallel group
                [step4, step5, step6],  # parallel group
            ])

            # Mixed serial and parallel
            pipeline = Pipeline([
                step1,          # serial
                [step2, step3], # parallel
                step4,          # serial
            ])
        """
        self.steps = steps
        self.config = config or PipelineConfig()
        self._executor = PipelineExecutor()

    def run(self, context: PipelineContext) -> PipelineContext:
        """
        Execute the pipeline and return final context.

        Args:
            context: Pipeline context containing shared data

        Returns:
            PipelineContext: Final context after all steps have executed

        Examples:
            final_context = pipeline.run(context)
            if final_context.errors:
                print("Pipeline had errors")
        """
        return self._executor.execute(self.steps, context, self.config)

    @staticmethod
    def create(
        steps: list[TaskStep], config: PipelineConfig | None = None
    ) -> "Pipeline":
        """
        Create a new pipeline (factory method following Log.create_logger pattern).

        Args:
            steps: List of pipeline steps
            config: Pipeline configuration (optional)

        Returns:
            Pipeline: Configured pipeline instance
        """
        return Pipeline(steps, config)
