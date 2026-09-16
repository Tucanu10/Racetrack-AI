play:
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
	make clean

run-web:
	@echo "Starting Local Web Dashboard..."
	@python.exe src/communication/dashboard_server.py
	make clean

train:
	make run-ai & make run-web & make run-ai-client
	make clean

clean:
	@echo "Cleaning cache files..."
	@rm -rf src/**/*__pycache__
	@rm -rf src/**/*.pyc
	@rm -rf src/**/*.class
	@rm -rf src/**/*.tmp
