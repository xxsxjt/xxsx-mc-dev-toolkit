package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.compat.ExampleModCompatFactory;
import io.zershyan.examplemod.registry.packet.ExampleRequestPacket;
import io.zershyan.examplemod.registry.packet.ExampleSyncPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

/**
 * 网络注册入口。
 *
 * <p>Forge 1.20.1 使用 {@link SimpleChannel}，没有 NeoForge 的 PayloadRegistrar。
 */
public final class ExampleModPackets {
    /** 协议版本取本 mod 版本（含构建数），不硬编码；两端不一致时拒绝连接 */
    private static final String PROTOCOL_VERSION = ModList.get()
            .getModContainerById(ExampleMod.MODID)
            .map(c -> c.getModInfo().getVersion().toString())
            .orElse("unknown");

    public static final SimpleChannel INSTANCE = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(ExampleMod.MODID, ExampleMod.MODID),
            () -> PROTOCOL_VERSION,
            PROTOCOL_VERSION::equals,
            PROTOCOL_VERSION::equals
    );

    private static int nextId = 0;

    private static int id() {
        return nextId++;
    }

    private ExampleModPackets() {
    }

    /** SimpleChannel 的注册不依赖事件总线，故无需入参 */
    public static void doRegister() {
        INSTANCE.messageBuilder(ExampleRequestPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(ExampleRequestPacket::new)
                .encoder(ExampleRequestPacket::encode)
                .consumerMainThread(ExampleRequestPacket::handle)
                .add();

        INSTANCE.messageBuilder(ExampleSyncPacket.class, id(), NetworkDirection.PLAY_TO_CLIENT)
                .decoder(ExampleSyncPacket::new)
                .encoder(ExampleSyncPacket::encode)
                .consumerMainThread(ExampleSyncPacket::handle)
                .add();

        ExampleModCompatFactory.registerNetwork(INSTANCE);
    }
}
