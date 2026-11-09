package io.zershyan.examplemod.registry.packet;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModAttachments;
import io.zershyan.examplemod.registry.ExampleModPackets;
import io.zershyan.examplemod.registry.attachment.ExampleStatusData;
import io.zershyan.forgeattachment.api.ForgeAttachmentApi;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.PacketDistributor;

import java.util.function.Supplier;

/** 客户端 → 服务端：请求服务端下发状态 */
public class ExampleRequestPacket {
    private final int requestId;

    public ExampleRequestPacket(int requestId) {
        this.requestId = requestId;
    }

    public ExampleRequestPacket(FriendlyByteBuf buf) {
        this.requestId = buf.readVarInt();
    }

    public void encode(FriendlyByteBuf buf) {
        buf.writeVarInt(requestId);
    }

    public void handle(Supplier<NetworkEvent.Context> supplier) {
        ServerPlayer sender = supplier.get().getSender();
        if (sender == null) return;
        if (requestId < 0) {
            ExampleMod.LOGGER.warn("Rejected request with negative id {}", requestId);
            return;
        }
        ExampleStatusData data = ForgeAttachmentApi.getData(sender, ExampleModAttachments.EXAMPLE_STATUS.get());
        int value = data == null ? 0 : data.getValue();
        ExampleModPackets.INSTANCE.send(PacketDistributor.PLAYER.with(() -> sender), new ExampleSyncPacket(value));
    }
}
