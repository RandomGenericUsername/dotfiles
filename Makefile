# Common modules directory
MODULES_DIR := src/common/modules

# List of all modules
MODULES := colorscheme-generator container-manager filesystem-path-builder hyprpaper-manager logging package-manager pipeline template-renderer wallpaper-effects-processor

# CLI directory
CLI_DIR := src/dotfiles-installer/cli

.PHONY: dev-shell sync-module sync-all-modules clean-cache help

dev-shell:
	@$(MAKE) -C $(CLI_DIR) dev-shell

sync-module: ## Sync a specific module (usage: make sync-module MODULE=filesystem-path-builder)
ifndef MODULE
	@echo "❌ Error: MODULE not specified"
	@echo "Usage: make sync-module MODULE=<module-name>"
	@echo ""
	@echo "Available modules:"
	@for module in $(MODULES); do \
		echo "  - $$module"; \
	done
	@exit 1
endif
	@if [ ! -d "$(MODULES_DIR)/$(MODULE)" ]; then \
		echo "❌ Error: Module '$(MODULE)' not found in $(MODULES_DIR)"; \
		echo ""; \
		echo "Available modules:"; \
		for module in $(MODULES); do \
			echo "  - $$module"; \
		done; \
		exit 1; \
	fi
	@echo "🔄 Syncing module: $(MODULE)"
	@cd $(CLI_DIR) && uv pip uninstall -y $(MODULE) 2>/dev/null || true
	@cd $(CLI_DIR) && uv pip install -e ../../common/modules/$(MODULE) --no-deps
	@echo "🔒 Updating lockfile..."
	@cd $(CLI_DIR) && uv lock
	@echo "✅ Module $(MODULE) synced successfully and lockfile updated"

sync-all-modules: ## Sync all common modules
	@echo "🔄 Syncing all modules..."
	@for module in $(MODULES); do \
		echo ""; \
		echo "📦 Syncing $$module..."; \
		(cd $(CLI_DIR) && uv pip uninstall -y $$module 2>/dev/null || true) && \
		(cd $(CLI_DIR) && uv pip install -e ../../common/modules/$$module --no-deps) || exit 1; \
	done
	@echo ""
	@echo "🔒 Updating lockfile..."
	@cd $(CLI_DIR) && uv lock
	@echo ""
	@echo "✅ All modules synced successfully and lockfile updated"

clean-cache: ## Clean Python cache files
	@echo "🧹 Cleaning Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cache cleaned"

help: ## Show this help message
	@echo "Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make sync-module MODULE=filesystem-path-builder"
	@echo "  make sync-all-modules"
	@echo "  make clean-cache"
