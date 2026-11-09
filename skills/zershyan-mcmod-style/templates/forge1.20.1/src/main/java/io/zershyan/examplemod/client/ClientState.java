package io.zershyan.examplemod.client;

public class ClientState {
    private static int value;

    public static int getValue() {
        return value;
    }

    public static void setValue(int value) {
        ClientState.value = value;
    }
}
