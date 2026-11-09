package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.compat.ExampleModCompatFactory;
import io.zershyan.examplemod.registry.packet.ExampleRequestPacket;
import io.zershyan.examplemod.registry.packet.ExampleSyncPacket;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.ModList;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;
import net.neoforged.neoforgespi.language.IModInfo;
import org.jetbrains.annotations.NotNull;

public final class ExampleModPackets {
    /** 协议版本取本 mod 版本（含构建数），不硬编码；两端不一致时 NeoForge 拒绝连接 */
    @NotNull
    private static final String PROTOCOL_VERSION = ModList.get()
            .getModContainerById(ExampleMod.MODID)
            .map(ModContainer::getModInfo)
            .map(IModInfo::getVersion)
            .map(Object::toString)
            .orElse("unknown");

    public static void doRegister(IEventBus modEventBus) {
        modEventBus.addListener(ExampleModPackets::register);
    }

    private static void register(RegisterPayloadHandlersEvent event) {
        PayloadRegistrar registrar = event.registrar(PROTOCOL_VERSION);
        // 处理器是 payload 自身的实例方法
        registrar.playToServer(ExampleRequestPacket.TYPE, ExampleRequestPacket.STREAM_CODEC, ExampleRequestPacket::handle);
        registrar.playToClient(ExampleSyncPacket.TYPE, ExampleSyncPacket.STREAM_CODEC, ExampleSyncPacket::handle);
        // 兼容层的 payload 由工厂统一注册
        ExampleModCompatFactory.registerNetwork(registrar);
    }
}
