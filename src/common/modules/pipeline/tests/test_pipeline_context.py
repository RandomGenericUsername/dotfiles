"""Tests for PipelineContext."""

from dotfiles_pipeline import PipelineContext


class TestPipelineContext:
    """Test suite for PipelineContext."""

    def test_context_creation_with_app_config(
        self, mock_app_config, mock_logger
    ):
        """Test creating context with app_config."""
        # Arrange & Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )

        # Assert
        assert context.app_config == mock_app_config
        assert context.app_config.name == "test_app"
        assert context.app_config.version == "1.0.0"

    def test_context_creation_with_logger(self, mock_app_config, mock_logger):
        """Test creating context with logger instance."""
        # Arrange & Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )

        # Assert
        assert context.logger_instance == mock_logger
        assert hasattr(context.logger_instance, "info")
        assert hasattr(context.logger_instance, "error")

    def test_context_results_dict_default(self, mock_app_config, mock_logger):
        """Test that results dict is initialized as empty."""
        # Arrange & Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )

        # Assert
        assert isinstance(context.results, dict)
        assert len(context.results) == 0

    def test_context_errors_list_default(self, mock_app_config, mock_logger):
        """Test that errors list is initialized as empty."""
        # Arrange & Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
        )

        # Assert
        assert isinstance(context.errors, list)
        assert len(context.errors) == 0

    def test_context_results_can_be_modified(self, pipeline_context):
        """Test that results dict can be modified."""
        # Arrange
        context = pipeline_context

        # Act
        context.results["key1"] = "value1"
        context.results["key2"] = 42
        context.results["key3"] = {"nested": "dict"}

        # Assert
        assert context.results["key1"] == "value1"
        assert context.results["key2"] == 42
        assert context.results["key3"] == {"nested": "dict"}
        assert len(context.results) == 3

    def test_context_errors_can_be_appended(self, pipeline_context):
        """Test that errors list can be appended to."""
        # Arrange
        context = pipeline_context
        error1 = RuntimeError("Error 1")
        error2 = ValueError("Error 2")

        # Act
        context.errors.append(error1)
        context.errors.append(error2)

        # Assert
        assert len(context.errors) == 2
        assert context.errors[0] == error1
        assert context.errors[1] == error2
        assert isinstance(context.errors[0], RuntimeError)
        assert isinstance(context.errors[1], ValueError)

    def test_context_with_custom_app_config(self, mock_logger):
        """Test context with custom app config type."""
        # Arrange
        from dataclasses import dataclass

        @dataclass
        class CustomConfig:
            setting1: str
            setting2: int

        custom_config = CustomConfig(setting1="test", setting2=100)

        # Act
        context = PipelineContext(
            app_config=custom_config,
            logger_instance=mock_logger,
        )

        # Assert
        assert context.app_config.setting1 == "test"
        assert context.app_config.setting2 == 100

    def test_context_results_dict_operations(self, pipeline_context):
        """Test various dict operations on results."""
        # Arrange
        context = pipeline_context

        # Act & Assert - Add items
        context.results["a"] = 1
        assert "a" in context.results

        # Update items
        context.results["a"] = 2
        assert context.results["a"] == 2

        # Delete items
        del context.results["a"]
        assert "a" not in context.results

        # Get with default
        value = context.results.get("nonexistent", "default")
        assert value == "default"

    def test_context_errors_list_operations(self, pipeline_context):
        """Test various list operations on errors."""
        # Arrange
        context = pipeline_context
        errors = [RuntimeError("E1"), ValueError("E2"), TypeError("E3")]

        # Act & Assert - Extend
        context.errors.extend(errors)
        assert len(context.errors) == 3

        # Index access
        assert context.errors[0].args[0] == "E1"
        assert context.errors[1].args[0] == "E2"

        # Slicing
        first_two = context.errors[:2]
        assert len(first_two) == 2

        # Clear
        context.errors.clear()
        assert len(context.errors) == 0

    def test_context_is_mutable(self, pipeline_context):
        """Test that context can be modified and changes persist."""
        # Arrange
        context = pipeline_context
        original_results_id = id(context.results)
        original_errors_id = id(context.errors)

        # Act
        context.results["test"] = "value"
        context.errors.append(RuntimeError("test"))

        # Assert - Same objects, modified in place
        assert id(context.results) == original_results_id
        assert id(context.errors) == original_errors_id
        assert len(context.results) == 1
        assert len(context.errors) == 1

    def test_context_with_prepopulated_results(
        self, mock_app_config, mock_logger
    ):
        """Test creating context with prepopulated results."""
        # Arrange
        initial_results = {"key1": "value1", "key2": 42}

        # Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
            results=initial_results,
        )

        # Assert
        assert context.results == initial_results
        assert context.results["key1"] == "value1"
        assert context.results["key2"] == 42

    def test_context_with_prepopulated_errors(
        self, mock_app_config, mock_logger
    ):
        """Test creating context with prepopulated errors."""
        # Arrange
        initial_errors = [RuntimeError("Error 1"), ValueError("Error 2")]

        # Act
        context = PipelineContext(
            app_config=mock_app_config,
            logger_instance=mock_logger,
            errors=initial_errors,
        )

        # Assert
        assert len(context.errors) == 2
        assert context.errors[0].args[0] == "Error 1"
        assert context.errors[1].args[0] == "Error 2"

    def test_context_generic_type_parameter(self, mock_logger):
        """Test that context works with generic type parameter."""
        # Arrange
        from dataclasses import dataclass

        @dataclass
        class SpecificConfig:
            value: str

        config = SpecificConfig(value="test")

        # Act
        context: PipelineContext[SpecificConfig] = PipelineContext(
            app_config=config,
            logger_instance=mock_logger,
        )

        # Assert
        assert context.app_config.value == "test"
        assert isinstance(context.app_config, SpecificConfig)
