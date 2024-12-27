.PHONY: pyclean create-ep-page create-ep-data create-ep-data-force test-openai

export PYTHONDONTWRITEBYTECODE=1

pyclean:
	@echo "Cleaning up __pycache__ directories and .pyc, .pyo, .pyd files..."
	@pycache_count=$$(find . -type d -name "__pycache__" | wc -l); \
	if [ $$pycache_count -eq 0 ]; then \
		echo "No __pycache__ directories found"; \
	else \
		echo "Found $$pycache_count __pycache__ directories"; \
		find . -type d -name "__pycache__" -exec rm -r {} +; \
	fi
	@pyc_count=$$(find . -type f -name "*.py[cod]" | wc -l); \
	if [ $$pyc_count -eq 0 ]; then \
		echo "No .pyc, .pyo, .pyd files found"; \
	else \
		echo "Found $$pyc_count .pyc, .pyo, .pyd files"; \
		find . -type f -name "*.py[cod]" -exec rm -f {} +; \
	fi
	@echo "Cleanup complete."


# create-ep-page: Generates an episode page for the given date.
# Usage:
#   epdate=2024-12-05 make create-ep-page
create-ep-page: 
	@if [ -z "$(epdate)" ]; then \
		echo "Error: epdate is not set. Usage: epdate=YYYY-MM-DD make create-ep-page"; \
		exit 1; \
	fi
	poetry run python -m gitp_acolyte.ceremonial.spells.episode_page.create_episode_page $(epdate)


# create-ref-ep-page: Generates an episode page for the given date.
# Usage:
#   make create-ref-ep-page
create-ref-ep-page: 
	poetry run python -m gitp_acolyte.ceremonial.spells.episode_page.create_episode_page --reference

# create-ep-page-force: Generates an episode page for the given date, forcing the creation of the page.
# Usage:
#   epdate=2024-12-05 make create-ep-page
create-ep-page-force: 
	@if [ -z "$(epdate)" ]; then \
		echo "Error: epdate is not set. Usage: epdate=YYYY-MM-DD make create-ep-page"; \
		exit 1; \
	fi
	poetry run python -m gitp_acolyte.ceremonial.spells.episode_page.create_episode_page $(epdate) --force

# create-ep-data: Generates episode data for the given date.
# Usage:
#   epdate=2024-12-05 make create-ep-data
create-ep-data:
	@if [ -z "$(epdate)" ]; then \
		echo "Error: epdate is not set. Usage: epdate=YYYY-MM-DD make create-ep-data"; \
		exit 1; \
	fi
	poetry run python -m gitp_acolyte.ceremonial.spells.episode_data.create $(epdate)

create-ep-data-reference:
	poetry run python -m gitp_acolyte.ceremonial.spells.episode_data.create --reference

# create-ep-data-ref-recreate: Generates episode data for the reference date, recreating the episode.yml file if it already exists.
# Usage:
#   make create-ep-data-ref-recreate
create-ep-data-ref-recreate:
	poetry run python -m gitp_acolyte.ceremonial.spells.episode_data.create --reference --recreate

# update-ep-data-file-attrs-reference: Updates the file attributes for the reference episode.
# Usage:
#   make update-ep-data-file-attrs-reference
update-ep-data-file-attrs-reference:
	poetry run python -m gitp_acolyte.ceremonial.spells.episode_data.update.file_attrs.update_file_attrs --reference

# update-ep-data-ref-recreate: Updates the file attributes for the reference episode, recreating the episode.yml file if it already exists.
# Usage:
#   make update-ep-data-ref-recreate
update-ep-data-ref-recreate:
	poetry run python -m gitp_acolyte.ceremonial.spells.episode_data.update.file_attrs.update_file_attrs --reference --recreate

# test-openai: Tests connectivity to the OpenAI API.
# Usage:
#   make test-openai
test-openai:
	poetry run python -m gitp_acolyte.utils.ai.test_openai

