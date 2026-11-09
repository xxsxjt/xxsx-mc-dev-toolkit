package io.zershyan.examplemod.registry.packet;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.client.ClientState;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.neoforged.neoforge.network.handling.IPayloadContext;
import org.jetbrains.annotations.NotNull;

/** 服务端 → 客户端：同步状态 */
public record ExampleSyncPacket(int value) implements CustomPacketPayload {
    public static final CustomPacketPayload.Type<ExampleSyncPacket> TYPE =
            new CustomPacketPayload.Type<>(ExampleMod.id("example_sync"));

    public static final StreamCodec<RegistryFriendlyByteBuf, ExampleSyncPacket> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.VAR_INT, ExampleSyncPacket::value,
            ExampleSyncPacket::new
    );

    @Override
    public @NotNull Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    /** 只在客户端侧执行；客户端只做展示 */
    public void handle(IPayloadContext context) {
        context.enqueueWork(() -> {
            Minecraft minecraft = Minecraft.getInstance();
            ClientLevel level = minecraft.level;
            LocalPlayer player = minecraft.player;
            if (level == null || player == null) return;
            ClientState.setValue(value);
        });
    }
}
