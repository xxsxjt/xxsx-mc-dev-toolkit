package io.zershyan.examplemod.registry.packet;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModAttachments;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.network.handling.IPayloadContext;
import org.jetbrains.annotations.NotNull;

/** 客户端 → 服务端：请求服务端下发状态 */
public record ExampleRequestPacket(int requestId) implements CustomPacketPayload {
    public static final CustomPacketPayload.Type<ExampleRequestPacket> TYPE =
            new CustomPacketPayload.Type<>(ExampleMod.id("example_request"));

    public static final StreamCodec<RegistryFriendlyByteBuf, ExampleRequestPacket> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.VAR_INT, ExampleRequestPacket::requestId,
            ExampleRequestPacket::new
    );

    @Override
    public @NotNull Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    /** 处理器写在 payload 自身，用实例访问器取字段，不额外传 payload 参数 */
    public void handle(IPayloadContext context) {
        context.enqueueWork(() -> {
            if (!(context.player() instanceof ServerPlayer player)) return;
            // 服务端基于自身状态重新校验，不信任客户端字段
            if (requestId < 0) {
                ExampleMod.LOGGER.warn("Rejected request with negative id {}", requestId);
                return;
            }
            int value = player.getData(ExampleModAttachments.EXAMPLE_STATUS.get()).getValue();
            PacketDistributor.sendToPlayer(player, new ExampleSyncPacket(value));
        });
    }
}
