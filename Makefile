run:
	@echo "Running the game..."
	@python.exe src/engine/racetrack.py
	make clean

run-ai:
	@echo "Compiling Java..."
	@javac.exe src/ai/*.java src/communication/*.java
	@echo "Starting Java Server..."
	@java.exe -cp src communication.Server
	make clean
	
run-ai-client:
	@echo "Running AI Client..."
	@python.exe src/engine/ai_racetrack.py

clean:
	@echo "Cleaning cache files..."
	@rm -rf src/**/*__pycache__
	@rm -rf src/**/*.class

run-web:
	@echo "Starting Local Web Dashboard..."
	@cd web && python.exe -m http.server 8000