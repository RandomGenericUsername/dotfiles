"""Default configuration values for colorscheme generator."""

from pathlib import Path

# Output defaults (OutputManager)
output_directory = Path.home() / ".cache/colorscheme"
default_formats = ["json", "sh", "css", "yaml"]

# Generation defaults
default_backend = "pywal"
default_color_count = 16
saturation_adjustment = 1.0

# Pywal backend defaults (color extraction)
pywal_cache_dir = Path.home() / ".cache/wal"  # Where pywal writes (read-only)
pywal_use_library = True

# Wallust backend defaults (color extraction)
wallust_output_format = "json"  # Parse JSON from stdout
wallust_backend_type = "resized"

# Custom backend defaults
custom_algorithm = "kmeans"
custom_n_clusters = 16

# Template defaults (OutputManager)
template_directory = Path("templates")
template_strict_mode = True

