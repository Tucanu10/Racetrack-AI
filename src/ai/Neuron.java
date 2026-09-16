package ai;

import java.io.Serializable;
import java.util.Random;

public class Neuron implements Serializable {
    private static final long serialVersionUID = 1L;
    private static final Random RANDOM = new Random();

    private double bias;
    public double[] weights;

    public Neuron(int numberOfInputs) {
        this.bias = RANDOM.nextDouble() * 2 - 1;
        weights = new double[numberOfInputs];
        double range = 1.0 / Math.sqrt(numberOfInputs);
        for (int i = 0; i < numberOfInputs; i++) {
            weights[i] = (RANDOM.nextDouble() * 2 - 1) * range;
        }
    }
    
    public void mutate() {
        if (RANDOM.nextDouble() < 0.2) {
            this.bias += (RANDOM.nextDouble() - 0.5) * 0.5;
        } else {
            int index = RANDOM.nextInt(weights.length);
            this.weights[index] += (RANDOM.nextDouble() - 0.5) * 0.5;
        }
    }

    public Neuron(Neuron copy) {
        this.bias = copy.bias;
        this.weights = copy.weights.clone();
    }

    public Neuron(Neuron n1, Neuron n2) {
        this.bias = RANDOM.nextBoolean() ? n1.bias : n2.bias;
        weights = new double[n1.weights.length];
        for (int i = 0; i < weights.length; i++) {
            weights[i] = RANDOM.nextBoolean() ? n1.weights[i] : n2.weights[i];
        }
    }

    public double compute(double... inputs) {
        if (inputs.length != weights.length) {
            throw new IllegalArgumentException("Neuron expected " + weights.length + " inputs, but got " + inputs.length);
        }
        double preActivation = this.bias;
        for (int i = 0; i < inputs.length; i++) {
            preActivation += this.weights[i] * inputs[i];
        }
        return Util.sigmoid(preActivation);
    }
}