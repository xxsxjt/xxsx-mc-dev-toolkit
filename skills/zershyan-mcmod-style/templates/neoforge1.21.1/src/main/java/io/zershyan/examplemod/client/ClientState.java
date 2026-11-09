package io.zershyan.examplemod.client;

/** 客户端侧缓存的同步状态 */
public final class ClientState {
    private static int value;

    private ClientState() {
    }

    public static int getValue() {
        return value;
    }

    public static void setValue(int newValue) {
        value = newValue;
    }
}
