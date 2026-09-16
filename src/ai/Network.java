package ai;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Network implements Serializable {
    private static final long serialVersionUID = 1L;
    private static final int INPUTS = 7;

    List<List<Neuron>> hiddenLayers = new ArrayList<>();
    List<Neuron> outputLayer = new ArrayList<>();

    // 1. Normal Constructor
    public Network(int numHiddenLayers, int neuronsPerLayer) {
        // Create the first hidden layer connected to the inputs
        List<Neuron> firstLayer = new ArrayList<>();
        for (int i = 0; i < neuronsPerLayer; i++) {
            firstLayer.add(new Neuron(INPUTS));
        }
        hiddenLayers.add(firstLayer);

        // Create subsequent hidden layers connected to the previous layer
        for (int l = 1; l < numHiddenLayers; l++) {
            List<Neuron> layer = new ArrayList<>();
            for (int i = 0; i < neuronsPerLayer; i++) {
                layer.add(new Neuron(neuronsPerLayer));
            }
            hiddenLayers.add(layer);
        }

        // Create output layer connected to the last hidden layer
        for (int i = 0; i < 2; i++) {
            outputLayer.add(new Neuron(neuronsPerLayer));
        }
    }

    public Network(Network copy) {
        // Deep copy all hidden layers
        for (List<Neuron> layer : copy.hiddenLayers) {
            List<Neuron> newLayer = new ArrayList<>();
            for (Neuron n : layer) {
                newLayer.add(new Neuron(n));
            }
            this.hiddenLayers.add(newLayer);
        }
        // Deep copy the output layer
        for (Neuron n : copy.outputLayer) {
            this.outputLayer.add(new Neuron(n));
        }
    }

    // 3. Mutate Method for deep layers
    private static final Random RANDOM = new Random();
    // Chance that any given neuron mutates. Mutating exactly one neuron per
    // call, regardless of network size, means a 2x6 network (~90 params) only
    // ever differs from its parent by a single weight or bias - far too
    // sparse to explore the space in a reasonable number of generations.
    private static final double MUTATION_RATE = 0.15;

    public void mutate() {
        boolean mutatedAny = false;
        for (List<Neuron> layer : hiddenLayers) {
            for (Neuron n : layer) {
                if (RANDOM.nextDouble() < MUTATION_RATE) {
                    n.mutate();
                    mutatedAny = true;
                }
            }
        }
        for (Neuron n : outputLayer) {
            if (RANDOM.nextDouble() < MUTATION_RATE) {
                n.mutate();
                mutatedAny = true;
            }
        }

        // Guarantee at least one mutation so "mutate()" never becomes a no-op
        if (!mutatedAny) {
            List<Neuron> allNeurons = new ArrayList<>();
            for (List<Neuron> layer : hiddenLayers) {
                allNeurons.addAll(layer);
            }
            allNeurons.addAll(outputLayer);
            allNeurons.get(RANDOM.nextInt(allNeurons.size())).mutate();
        }
    }

    // 4. Predict Method
    public double[] predict(double... inputs) {
        double[] currentInputs = inputs;
        List<double[]> allHiddenOutputs = new ArrayList<>();

        // Feed forward through all hidden layers
        for (List<Neuron> layer : hiddenLayers) {
            double[] nextInputs = new double[layer.size()];
            for (int i = 0; i < layer.size(); i++) {
                nextInputs[i] = layer.get(i).compute(currentInputs);
            }
            allHiddenOutputs.add(nextInputs);
            currentInputs = nextInputs;
        }

        // Compute final outputs
        double outSteering = outputLayer.get(0).compute(currentInputs);
        double outThrottle = outputLayer.get(1).compute(currentInputs);

        // Layout: [steering, throttle, numHiddenLayers, layer0Size, layer0..., layer1Size, layer1..., ...]
        // This carries every neuron in every hidden layer instead of a fixed
        // 3-value slice of just the first layer, so the dashboard can draw
        // the network's true shape.
        int total = 3 + allHiddenOutputs.size();
        for (double[] layerOut : allHiddenOutputs) total += layerOut.length;

        double[] result = new double[total];
        result[0] = outSteering;
        result[1] = outThrottle;
        result[2] = allHiddenOutputs.size();
        int idx = 3;
        for (double[] layerOut : allHiddenOutputs) {
            result[idx++] = layerOut.length;
            for (double v : layerOut) result[idx++] = v;
        }
        return result;
    }
    
    // 5. Save and Load methods
    public void save(String filepath) {
        try (ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(filepath))) {
            out.writeObject(this);
            System.out.println("Network saved to " + filepath);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static Network load(String filepath) {
        try (ObjectInputStream in = new ObjectInputStream(new FileInputStream(filepath))) {
            System.out.println("Save found! Network loaded.");
            return (Network) in.readObject();
        } catch (Exception e) {
            System.out.println("No save found. Starting fresh.");
            return new Network(2, 6);
        }
    }
}