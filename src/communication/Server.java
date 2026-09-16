package communication;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import ai.Network;

public class Server {
    private static final int POPULATION_SIZE = 100;
    private static final int ELITE_COUNT = 10;

    static class Candidate implements Comparable<Candidate> {
        Network network;
        double fitness;

        Candidate(Network network, double fitness) {
            this.network = network;
            this.fitness = fitness;
        }

        @Override
        public int compareTo(Candidate other) {
            return Double.compare(other.fitness, this.fitness); // Descending order
        }
    }

    public static void main(String[] args) {
        List<Network> population = new ArrayList<>();
        for (int i = 0; i < POPULATION_SIZE; i++) {
            population.add(new Network(2, 6)); // 2 hidden layers, 6 neurons each
        }

        try (ServerSocket serverSocket = new ServerSocket(8080)) {
            System.out.println("Population server listening on port 8080");
            Socket clientSocket = serverSocket.accept();
            System.out.println("Client connected: " + clientSocket.getInetAddress());

            BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);

            String line;
            while ((line = in.readLine()) != null) {
                if (line.equals("SAVE")) {
                    population.get(0).save("champion.dat"); // Saves top performer
                    continue;
                }
                
                if (line.equals("LOAD")) {
                    Network loaded = Network.load("champion.dat");
                    for (int i = 0; i < POPULATION_SIZE; i++) {
                        population.set(i, new Network(loaded));
                        if (i > 0) population.get(i).mutate(); // Mutate clones to keep variation
                    }
                    System.out.println("Loaded champion to population.");
                    continue;
                }
                
                if (line.startsWith("EPOCH_END:")) {
                    String[] rawScores = line.substring("EPOCH_END:".length()).split(",");
                    List<Candidate> candidates = new ArrayList<>();

                    for (int i = 0; i < POPULATION_SIZE; i++) {
                        double fit = Double.parseDouble(rawScores[i]);
                        candidates.add(new Candidate(population.get(i), fit));
                    }

                    Collections.sort(candidates);
                    double best = candidates.get(0).fitness;
                    double worst = candidates.get(candidates.size() - 1).fitness;
                    double avg = candidates.stream().mapToDouble(c -> c.fitness).average().orElse(0.0);
                    System.out.printf("Epoch finished. Best: %.2f | Avg: %.2f | Worst: %.2f%n", best, avg, worst);

                    List<Network> nextGen = new ArrayList<>();
                    // Keep the top elites
                    for (int i = 0; i < ELITE_COUNT; i++) {
                        nextGen.add(new Network(candidates.get(i).network));
                    }

                    // Breed remaining spots from elites
                    for (int i = ELITE_COUNT; i < POPULATION_SIZE; i++) {
                        Network parent = candidates.get(i % ELITE_COUNT).network;
                        Network child = new Network(parent);
                        child.mutate();
                        nextGen.add(child);
                    }

                    population = nextGen;
                    out.println("READY");
                    continue;
                }

                String[] carsData = line.split("\\|");
                StringBuilder response = new StringBuilder();

                for (int i = 0; i < carsData.length; i++) {
                    // Extract the car ID
                    String carEntry = carsData[i];
                    int colonIdx = carEntry.indexOf(':');
                    int carId = Integer.parseInt(carEntry.substring(0, colonIdx));
                    
                    // Extract the sensor array
                    String[] sensorStrs = carEntry.substring(colonIdx + 1).split(",");
                    double[] sensors = new double[sensorStrs.length];
                    for (int s = 0; s < sensorStrs.length; s++) {
                        sensors[s] = Double.parseDouble(sensorStrs[s]);
                    }
                    
                    // Feed forward through the network
                    double[] cmds = population.get(carId).predict(sensors);

                    if (i > 0) response.append("|");

                    // Send every value predict() produced: steering, throttle,
                    // then the layer-count-prefixed hidden-layer activations.
                    response.append(carId).append(":");
                    for (int v = 0; v < cmds.length; v++) {
                        if (v > 0) response.append(",");
                        response.append(cmds[v]);
                    }
                }

                out.println(response.toString());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}