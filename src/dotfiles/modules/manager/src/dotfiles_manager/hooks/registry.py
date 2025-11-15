"""Hook registry with pipeline-based execution."""

from dotfiles_pipeline import (
    Pipeline,
    PipelineConfig,
    PipelineContext,
    PipelineStep,
)

from dotfiles_manager.hooks.base import Hook
from dotfiles_manager.models.hook import HookContext, HookResult


class HookStep(PipelineStep):
    """Adapter to make Hook compatible with PipelineStep."""

    def __init__(self, hook: Hook, hook_config: dict):
        """Initialize hook step.

        Args:
            hook: Hook instance to execute
            hook_config: Hook-specific configuration
        """
        self._hook = hook
        self._hook_config = hook_config

    @property
    def step_id(self) -> str:
        """Unique identifier for this step."""
        return self._hook.name

    @property
    def description(self) -> str:
        """Human-readable description."""
        return f"Hook: {self._hook.name}"

    @property
    def critical(self) -> bool:
        """Get criticality from hook config."""
        return self._hook_config.get("critical", False)

    def run(self, context: PipelineContext) -> PipelineContext:
        """Execute hook and store result in context.

        Args:
            context: Pipeline context

        Returns:
            PipelineContext: Modified context with hook result
        """
        hook_context: HookContext = context.results["hook_context"]
        hook_context.config = self._hook_config

        result = self._hook.execute(hook_context)

        # Store result
        if "hook_results" not in context.results:
            context.results["hook_results"] = {}
        context.results["hook_results"][self._hook.name] = result

        return context


class HookRegistry:
    """Manages hook registration and execution using pipeline."""

    def __init__(self, config: dict, app_config=None, logger=None):
        """Initialize hook registry.

        Args:
            config: Hook configuration from settings.toml
            app_config: Application configuration (optional, can be set later)
            logger: Logger instance (optional, can be set later)
        """
        self._hooks: dict[str, Hook] = {}
        self._config = config
        self._app_config = app_config
        self._logger = logger

    def register(self, hook: Hook) -> None:
        """Register a hook.

        Args:
            hook: Hook instance to register
        """
        self._hooks[hook.name] = hook

    def execute_all(self, hook_context: HookContext) -> dict[str, HookResult]:
        """Execute hooks using pipeline with mixed serial/parallel execution.

        Args:
            hook_context: Context to pass to hooks

        Returns:
            Dict mapping hook name to result
        """
        # Build pipeline steps based on configuration
        steps = self._build_pipeline_steps()

        if not steps:
            return {}

        # Create a minimal logger if none provided
        if self._logger is None:
            from dotfiles_logging import Log, LogLevels

            logger = Log.create_logger(
                "hook_registry", log_level=LogLevels.INFO
            )
        else:
            logger = self._logger

        # Create pipeline context with required parameters
        pipeline_context = PipelineContext(
            app_config=self._app_config or {},  # Use empty dict if no config
            logger_instance=logger,
            results={"hook_context": hook_context, "hook_results": {}},
        )

        # Create pipeline config
        pipeline_config = PipelineConfig(
            fail_fast=self._config.get("fail_fast", False),
        )

        # Execute pipeline
        pipeline = Pipeline(steps, pipeline_config)
        final_context = pipeline.run(pipeline_context)

        return final_context.results.get("hook_results", {})

    def _build_pipeline_steps(
        self,
    ) -> list[HookStep | list[HookStep]]:
        """Build pipeline steps from hook configuration.

        Returns:
            List of steps (serial) or lists of steps (parallel groups)
        """
        enabled_hooks = self._config.get("enabled", [])
        execution_groups = self._config.get("execution_groups", [])

        # If no execution groups defined, create default serial execution
        if not execution_groups:
            execution_groups = [{"hooks": enabled_hooks, "mode": "serial"}]

        steps: list[HookStep | list[HookStep]] = []

        for group in execution_groups:
            group_hooks = group.get("hooks", [])
            mode = group.get("mode", "serial")

            # Filter to only enabled hooks
            group_hooks = [h for h in group_hooks if h in enabled_hooks]

            if not group_hooks:
                continue

            # Create hook steps
            hook_steps = []
            for hook_name in group_hooks:
                if hook_name not in self._hooks:
                    continue

                hook = self._hooks[hook_name]
                hook_config = self._config.get(hook_name, {})
                hook_steps.append(HookStep(hook, hook_config))

            if not hook_steps:
                continue

            # Add to pipeline based on mode
            if mode == "parallel":
                # Parallel group
                steps.append(hook_steps)
            else:
                # Serial - add each step individually
                steps.extend(hook_steps)

        return steps
