.PHONY: pyclean

pyclean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.py[cod]" -exec rm -f {} +
