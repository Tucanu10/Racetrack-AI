<div align="center">
  <h1>Racetrack<kbd>AI</kbd></h1>
  <p><b>Self-Learning Neural Network & Autonomous Racing Simulation</b></p>
  <p><i>A hybrid Java and Python machine learning framework that trains autonomous agents to navigate a 2D racing circuit using a Multi-Layer Perceptron (MLP) neural network evolved through a genetic algorithm.</i></p>
</div>

---

## System Architecture

Racetrack AI integrates a real-time game simulation environment with a concurrent Java backend server. The system evaluates a population of candidate neural networks across generations, selecting top performers (elites) and applying crossover and mutation operators to optimize driving strategies. 

The architecture is divided into three core components:

<table>
  <tr>
    <td width="33%" valign="top">
      <h3>☕ Java Backend</h3>
      <b>Neural Network:</b> Custom feed-forward MLP (<code>Network.java</code>, <code>Neuron.java</code>, <code>Util.java</code>) supporting configurable hidden layers, sigmoid activation functions, weight cloning, uniform crossover, and mutation logic.<br><br>
      <b>Evolutionary Server:</b> (<code>Server.java</code>) Manages a population of 200 candidates per generation. Evaluates fitness scores, handles elitism, coordinates genetic breeding, and serializes top models to <code>champion.dat</code>.<br><br>
      <b>Socket Comm:</b> TCP server listening on port <code>8081</code> handling batch vector predictions and control commands.
    </td>
    <td width="33%" valign="top">
      <h3>🐍 Python Simulation</h3>
      <b>Game Engine:</b> (<code>game.py</code>, <code>racetrack.py</code>, <code>ai_racetrack.py</code>) Built with Pygame to handle collision detection, checkpoint progression, physics calculations, and window rendering.<br><br>
      <b>Sensor Engine:</b> (<code>raycasting.py</code>) Casts seven directional rays (-45 degrees to +45 degrees) from the vehicle to compute distances to track boundaries. This is paired with speed and checkpoint angle normalization.
    </td>
    <td width="33%" valign="top">
      <h3>🌐 Web Telemetry</h3>
      <b>Dashboard:</b> An HTTP Server & Client (<code>dashboard_server.py</code>) serves a static HTML dashboard via <code>index.html</code>.<br><br>
      <b>Real-Time Stats:</b> Communicates with the simulation state via periodic <code>state.json</code> updates so telemetry data and neural activation weights can be monitored live.
    </td>
  </tr>
</table>

---

## To learn more about making custom maps and how to train the neural network, check out the [Map Making Guide](docs/map-guide.md)