run:
	@echo "Running the game..."
	@python.exe src/engine/racetrack.py
	@echo "Cleaning cache files..."
	@rm -rf src/**/*__pycache__