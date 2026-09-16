package ai;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Network implements Serializable {
    private static final long serialVersionUID = 1L;
    private static final int INPUTS = 9;

    List<List<Neuron>> hiddenLayers = new ArrayList<>();
    List<Neuron> outputLayer = new ArrayList<>();

    public Network(int numHiddenLayers, int neuronsPerLayer) {
        List<Neuron> firstLayer = new ArrayList<>();
        for (int i = 0; i < neuronsPerLayer; i++) {
            firstLayer.add(new Neuron(INPUTS));
        }
        hiddenLayers.add(firstLayer);

        for (int l = 1; l < numHiddenLayers; l++) {
            List<Neuron> layer = new ArrayList<>();
            for (int i = 0; i < neuronsPerLayer; i++) {
                layer.add(new Neuron(neuronsPerLayer));
            }
            hiddenLayers.add(layer);
        }

        for (int i = 0; i < 2; i++) {
            outputLayer.add(new Neuron(neuronsPerLayer));
        }
    }

    // Constructor de copiere
    public Network(Network copy) {
        for (List<Neuron> layer : copy.hiddenLayers) {
            List<Neuron> newLayer = new ArrayList<>();
            for (Neuron n : layer) {
                newLayer.add(new Neuron(n));
            }
            this.hiddenLayers.add(newLayer);
        }
        for (Neuron n : copy.outputLayer) {
            this.outputLayer.add(new Neuron(n));
        }
    }

    public Network(Network p1, Network p2) {
        for (int l = 0; l < p1.hiddenLayers.size(); l++) {
            List<Neuron> layer1 = p1.hiddenLayers.get(l);
            List<Neuron> layer2 = p2.hiddenLayers.get(l);
            List<Neuron> newLayer = new ArrayList<>();
            for (int i = 0; i < layer1.size(); i++) {
                newLayer.add(new Neuron(layer1.get(i), layer2.get(i)));
            }
            this.hiddenLayers.add(newLayer);
        }
        for (int i = 0; i < p1.outputLayer.size(); i++) {
            this.outputLayer.add(new Neuron(p1.outputLayer.get(i), p2.outputLayer.get(i)));
        }
    }

    private static final Random RANDOM = new Random();

    public void mutate(double mutationRate) {
        boolean mutatedAny = false;
        for (List<Neuron> layer : hiddenLayers) {
            for (Neuron n : layer) {
                if (RANDOM.nextDouble() < mutationRate) {
                    n.mutate();
                    mutatedAny = true;
                }
            }
        }
        for (Neuron n : outputLayer) {
            if (RANDOM.nextDouble() < mutationRate) {
                n.mutate();
                mutatedAny = true;
            }
        }

        if (!mutatedAny) {
            List<Neuron> allNeurons = new ArrayList<>();
            for (List<Neuron> layer : hiddenLayers) {
                allNeurons.addAll(layer);
            }
            allNeurons.addAll(outputLayer);
            allNeurons.get(RANDOM.nextInt(allNeurons.size())).mutate();
        }
    }

    public double[] predict(double... inputs) {
        double[] currentInputs = inputs;
        List<double[]> allHiddenOutputs = new ArrayList<>();

        for (List<Neuron> layer : hiddenLayers) {
            double[] nextInputs = new double[layer.size()];
            for (int i = 0; i < layer.size(); i++) {
                nextInputs[i] = layer.get(i).compute(currentInputs);
            }
            allHiddenOutputs.add(nextInputs);
            currentInputs = nextInputs;
        }

        double outSteering = outputLayer.get(0).compute(currentInputs);
        double outThrottle = outputLayer.get(1).compute(currentInputs);

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
            return new Network(2, 10); // 2 hidden layers, 10 neurons each
        }
    }
}