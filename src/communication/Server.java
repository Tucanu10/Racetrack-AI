package communication;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import ai.Network;
import engine.Config;

public class Server {
    private static final int POPULATION_SIZE = 300;
    private static final int ELITE_COUNT = POPULATION_SIZE / 10;
    private static final float MUTATION_RATE = Config.MUTATION_RATE;

    private static final Object POPULATION_LOCK = new Object();
    private static List<Network> population = new ArrayList<>();

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
        synchronized (POPULATION_LOCK) {
            for (int i = 0; i < POPULATION_SIZE; i++) {
                population.add(new Network(2, 10)); // 2 hidden layers, 10 neurons each
            }
        }

        try (ServerSocket serverSocket = new ServerSocket(Config.COMMUNICATION_PORT)) {
            System.out.println("Population server listening on port " + Config.COMMUNICATION_PORT);
            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("Client connected: " + clientSocket.getInetAddress());
                Thread handler = new Thread(() -> handleClient(clientSocket));
                handler.setDaemon(true);
                handler.start();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void handleClient(Socket clientSocket) {
        try (
            BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true)
        ) {
            String line;
            while ((line = in.readLine()) != null) {
                if (line.equals("SAVE")) {
                    synchronized (POPULATION_LOCK) {
                        population.get(0).save("champion.dat"); // Saves top performer
                    }
                    out.println("SAVED");
                    continue;
                }

                if (line.equals("LOAD")) {
                    synchronized (POPULATION_LOCK) {
                        Network loaded = Network.load("champion.dat");
                        for (int i = 0; i < POPULATION_SIZE; i++) {
                            population.set(i, new Network(loaded));
                        }
                    }
                    System.out.println("Loaded champion to population.");
                    out.println("LOADED");
                    continue;
                }

                if (line.equals("RESET")) {
                    synchronized (POPULATION_LOCK) {
                        population.clear();
                        for (int i = 0; i < POPULATION_SIZE; i++) {
                            population.add(new Network(2, 10)); // 2 hidden layers, 10 neurons each
                            if(i < POPULATION_SIZE / 5)
                            population.get(i).mutate(MUTATION_RATE); // Mutate all but the first
                        }
                    }
                    System.out.println("Population reset.");
                    out.println("RESET_OK");
                    continue;
                }

                if (line.startsWith("EPOCH_END:")) {
                    String[] rawScores = line.substring("EPOCH_END:".length()).split(",");

                    synchronized (POPULATION_LOCK) {
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

                        double mutationRate = (best - avg < 50.0) ? 0.35 : 0.20;

                        List<Network> nextGen = new ArrayList<>();
                        for (int i = 0; i < ELITE_COUNT; i++) {
                            nextGen.add(new Network(candidates.get(i).network));
                        }

                        Random rand = new Random();
                        for (int i = ELITE_COUNT; i < POPULATION_SIZE; i++) {
                            Network parent1 = candidates.get(rand.nextInt(ELITE_COUNT)).network;
                            Network parent2 = candidates.get(rand.nextInt(ELITE_COUNT)).network;
                            Network child = new Network(parent1, parent2);
                            child.mutate(mutationRate);
                            nextGen.add(child);
                        }
                        population = nextGen;
                    }

                    out.println("READY");
                    continue;
                }

                // Batch prediction request
                String[] carsData = line.split("\\|");
                StringBuilder response = new StringBuilder();

                synchronized (POPULATION_LOCK) {
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

                        response.append(carId).append(":");
                        for (int v = 0; v < cmds.length; v++) {
                            if (v > 0) response.append(",");
                            response.append(cmds[v]);
                        }
                    }
                }

                out.println(response.toString());
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                clientSocket.close();
            } catch (Exception ignored) {
            }
        }
    }
}
