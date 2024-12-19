.PHONY: pyclean create-ep-page

export PYTHONDONTWRITEBYTECODE=1

pyclean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.py[cod]" -exec rm -f {} +


# create-ep-page: Generates an episode page for the given date.
# Usage:
#   epdate=2024-12-05 make create-ep-page
create-ep-page: 
	@if [ -z "$(epdate)" ]; then \
		echo "Error: epdate is not set. Usage: epdate=YYYY-MM-DD make create-ep-page"; \
		exit 1; \
	fi
	poetry run python -m gitp_acolyte.ceremonial.spells.episode_page.create_episode_page $(epdate)
