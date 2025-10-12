"""Parallel task executor using ThreadPoolExecutor."""

import copy
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.modules.pipeline.core.types import (
    LogicOperator,
    ParallelConfig,
    PipelineContext,
    PipelineStep,
)
from src.modules.pipeline.executors.task_executor import TaskExecutor


class ParallelTaskExecutor:
    """Executes parallel step groups with configurable logic and context merging."""

    def __init__(self, task_executor: TaskExecutor | None = None):
        """
        Initialize parallel executor.

        Args:
            task_executor: Task executor for individual steps (optional)
        """
        self.task_executor = task_executor or TaskExecutor()

    def execute(
        self,
        steps: list[PipelineStep],
        context: PipelineContext,
        config: ParallelConfig,
    ) -> PipelineContext:
        """
        Execute a group of steps in parallel with context merging.

        Args:
            steps: List of pipeline steps to execute in parallel
            context: Pipeline context
            config: Parallel execution configuration

        Returns:
            PipelineContext: Merged context from all parallel executions
        """
        if not steps:
            return context

        # Keep original context for merging
        original_context = copy.deepcopy(context)

        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            # Submit all steps with deep copies of context
            futures = [
                executor.submit(
                    self.task_executor.execute,
                    step,
                    copy.deepcopy(original_context),
                )
                for step in steps
            ]

            # Collect results
            step_contexts = []
            step_success = []

            for future in as_completed(futures, timeout=config.timeout):
                try:
                    result_context = future.result()
                    step_contexts.append(result_context)
                    step_success.append(True)
                except Exception:
                    step_success.append(False)

            # Check if parallel group succeeded based on logic operator
            if config.operator == LogicOperator.AND:
                group_succeeded = all(step_success)
            else:  # OR
                group_succeeded = any(step_success)

            if not group_succeeded:
                raise RuntimeError("Parallel group failed")

            # Merge contexts from successful steps
            merged_context = self._merge_contexts(
                original_context, step_contexts
            )
            return merged_context

    def _merge_contexts(
        self,
        original_context: PipelineContext,
        step_contexts: list[PipelineContext],
    ) -> PipelineContext:
        """
        Merge contexts from parallel steps.

        Args:
            original_context: The original context before parallel execution
            step_contexts: List of contexts returned from parallel steps

        Returns:
            PipelineContext: Merged context
        """
        merged = copy.deepcopy(original_context)

        for step_context in step_contexts:
            # Merge results if both contexts have results attribute
            if hasattr(merged, "results") and hasattr(step_context, "results"):
                if isinstance(merged.results, dict) and isinstance(
                    step_context.results, dict
                ):
                    # Dict-style results - merge with special handling for numeric values
                    for key, value in step_context.results.items():
                        original_value = (
                            original_context.results.get(key, 0)
                            if hasattr(original_context, "results")
                            else 0
                        )

                        if isinstance(value, (int, float)) and isinstance(
                            original_value, (int, float)
                        ):
                            # For numeric values, calculate the increment from this step
                            step_increment = value - original_value
                            if (
                                step_increment > 0
                            ):  # Only add positive increments
                                merged.results[key] = (
                                    merged.results.get(key, original_value)
                                    + step_increment
                                )
                        else:
                            # For non-numeric values, just update
                            merged.results[key] = value
                elif isinstance(merged.results, list) and isinstance(
                    step_context.results, list
                ):
                    # List-style results - only add new items (items not in original)
                    original_len = (
                        len(original_context.results)
                        if hasattr(original_context, "results")
                        else 0
                    )
                    new_items = step_context.results[
                        original_len:
                    ]  # Only new items added by this step
                    merged.results.extend(new_items)

            # Merge errors if both contexts have errors attribute
            if hasattr(merged, "errors") and hasattr(step_context, "errors"):
                original_error_len = (
                    len(original_context.errors)
                    if hasattr(original_context, "errors")
                    else 0
                )
                new_errors = step_context.errors[
                    original_error_len:
                ]  # Only new errors
                merged.errors.extend(new_errors)

        return merged
