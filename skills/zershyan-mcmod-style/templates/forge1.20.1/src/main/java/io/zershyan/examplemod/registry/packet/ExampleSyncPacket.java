package io.zershyan.examplemod.registry.packet;

import io.zershyan.examplemod.client.ClientState;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** 服务端 → 客户端：同步状态；客户端只做展示 */
public class ExampleSyncPacket {
    private final int value;

    public ExampleSyncPacket(int value) {
        this.value = value;
    }

    public ExampleSyncPacket(FriendlyByteBuf buf) {
        this.value = buf.readVarInt();
    }

    public void encode(FriendlyByteBuf buf) {
        buf.writeVarInt(value);
    }

    public void handle(Supplier<NetworkEvent.Context> supplier) {
        ClientState.setValue(value);
    }
}
