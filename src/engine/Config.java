package engine;

import java.io.FileInputStream;
import java.util.Properties;

public class Config {
    public static String ACTIVE_MAP;
    public static int COMMUNICATION_PORT;
    public static int DASH_PORT;

    static {
        Properties prop = new Properties();
        try (FileInputStream input = new FileInputStream("config.properties")) {
            prop.load(input);
            ACTIVE_MAP = prop.getProperty("ACTIVE_MAP", "map0");
            COMMUNICATION_PORT = Integer.parseInt(prop.getProperty("COMMUNICATION_PORT", "8081"));
            DASH_PORT = Integer.parseInt(prop.getProperty("DASH_PORT", "8080"));
        } catch (Exception e) {
            System.out.println("Could not load config.properties, using defaults.");
        }
    }
}