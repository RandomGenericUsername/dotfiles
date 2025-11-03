"""Effect pipeline for chaining multiple effects."""

import tempfile
from pathlib import Path

from PIL import Image

from wallpaper_processor.config.enums import ProcessingMode
from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.exceptions import ProcessingError
from wallpaper_processor.core.types import (
    EffectMetadata,
    EffectParams,
    ProcessingMetadata,
    ProcessorConfig,
)


class EffectPipeline:
    """Chain multiple effects together."""

    def __init__(
        self,
        effects: list[tuple[WallpaperEffect, EffectParams]],
        config: ProcessorConfig | None = None,
    ):
        """Initialize pipeline.

        Args:
            effects: List of (effect, params) tuples
            config: Processing configuration (uses defaults if None)
        """
        self.effects = effects
        self.config = config or ProcessorConfig()
        self.metadata: ProcessingMetadata | None = None

    def apply(self, input_path: Path, output_path: Path) -> Path:
        """Apply all effects in sequence.

        Args:
            input_path: Input image path
            output_path: Output image path

        Returns:
            Path to output file

        Raises:
            FileNotFoundError: If input file doesn't exist
            ProcessingError: If any effect fails
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Ensure all effects are available
        for effect, _ in self.effects:
            effect.ensure_available()

        # Choose processing mode
        if self.config.processing_mode == ProcessingMode.MEMORY:
            result_path = self._apply_memory(input_path, output_path)
        else:
            result_path = self._apply_file(input_path, output_path)

        # Build metadata
        effects_metadata = [
            EffectMetadata(
                name=effect.effect_name,
                backend=effect.backend_name,
                params=params.model_dump(),
            )
            for effect, params in self.effects
        ]

        self.metadata = ProcessingMetadata(
            input_path=input_path,
            output_path=output_path,
            effects_applied=effects_metadata,
            processing_mode=self.config.processing_mode,
            output_format=self.config.output_format,
            quality=self.config.quality,
        )

        # Write metadata if requested
        if self.config.write_metadata:
            self._write_metadata(output_path)

        return result_path

    def _apply_memory(self, input_path: Path, output_path: Path) -> Path:
        """Apply effects in memory (fast).

        Args:
            input_path: Input image path
            output_path: Output image path

        Returns:
            Path to output file
        """
        image = Image.open(input_path)

        # Apply each effect in sequence
        for effect, params in self.effects:
            try:
                image = effect.apply(image, params)
            except Exception as e:
                raise ProcessingError(
                    f"Failed to apply {effect.effect_name} ({effect.backend_name}): {e}"
                ) from e

        # Save with configured format and quality
        save_kwargs = {}
        if self.config.output_format.value in ("jpg", "jpeg", "webp"):
            save_kwargs["quality"] = self.config.quality

        image.save(output_path, **save_kwargs)
        return output_path

    def _apply_file(self, input_path: Path, output_path: Path) -> Path:
        """Apply effects file-by-file (memory efficient).

        Args:
            input_path: Input image path
            output_path: Output image path

        Returns:
            Path to output file
        """
        current_input = input_path
        temp_files: list[Path] = []

        try:
            for i, (effect, params) in enumerate(self.effects):
                # Last effect writes to final output
                if i == len(self.effects) - 1:
                    current_output = output_path
                else:
                    # Create temp file for intermediate result
                    temp_fd, temp_name = tempfile.mkstemp(suffix=".png")
                    import os

                    os.close(temp_fd)  # Close file descriptor
                    current_output = Path(temp_name)
                    temp_files.append(current_output)

                try:
                    effect.apply_to_file(current_input, current_output, params)
                except Exception as e:
                    raise ProcessingError(
                        f"Failed to apply {effect.effect_name} ({effect.backend_name}): {e}"
                    ) from e

                # Update input for next iteration
                current_input = current_output

            return output_path

        finally:
            # Clean up temp files
            for temp_file in temp_files:
                temp_file.unlink(missing_ok=True)

    def _write_metadata(self, output_path: Path) -> None:
        """Write metadata to JSON file.

        Args:
            output_path: Output image path (metadata will be written alongside)
        """
        if self.metadata is None:
            return

        import json

        metadata_path = (
            output_path.parent / f"{output_path.stem}_metadata.json"
        )

        # Convert metadata to dict
        metadata_dict = self.metadata.model_dump(mode="json")

        # Convert Path objects to strings
        metadata_dict["input_path"] = str(metadata_dict["input_path"])
        metadata_dict["output_path"] = str(metadata_dict["output_path"])

        with open(metadata_path, "w") as f:
            json.dump(metadata_dict, f, indent=2)

    def get_metadata(self) -> ProcessingMetadata | None:
        """Get processing metadata.

        Returns:
            ProcessingMetadata if pipeline has been applied, None otherwise
        """
        return self.metadata
