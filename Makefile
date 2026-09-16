play:
	@echo "Running the game..."
	@python.exe src/engine/racetrack.py
	@$(MAKE) clean

run-ai:
	@echo "Compiling Java..."
	@javac.exe src/**/*.java
	@echo "Starting Java Server..."
	@java.exe -cp src communication.Server
	@$(MAKE) clean

run-ai-client:
	@echo "Running AI Client..."
	@python.exe src/engine/ai_racetrack.py
	@$(MAKE) clean

run-web:
	@echo "Starting Local Web Dashboard..."
	@python.exe src/communication/dashboard_server.py
	@$(MAKE) clean

train:
	@echo "Compiling Java..."
	@javac.exe src/**/*.java
	@echo "Starting Training Environment..."
	@bash -c ' \
		java.exe -cp src communication.Server & JAVA_PID=$$!; \
		python.exe src/communication/dashboard_server.py & WEB_PID=$$!; \
		trap "kill -9 $$JAVA_PID $$WEB_PID 2>/dev/null || true" EXIT INT TERM; \
		python.exe src/engine/ai_racetrack.py \
	'
	@$(MAKE) clean

clean:
	@echo "Cleaning cache files..."
	@rm -rf src/**/*__pycache__
	@rm -rf src/**/*.pyc
	@rm -rf src/**/*.class
	@rm -rf src/**/*.tmp