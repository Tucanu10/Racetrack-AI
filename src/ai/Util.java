package ai;

public class Util {
    public static double sigmoid(double x) {
        return 1 / (1 + Math.exp(-x));
    }
}
