package io.zershyan.examplemod.handler.client;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModKeyMappings;
import io.zershyan.examplemod.registry.packet.ExampleRequestPacket;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/** 按键回调与客户端 tick 逻辑 */
public final class KeyPressHandler {

    private KeyPressHandler() {
    }

    @EventBusSubscriber(modid = ExampleMod.MODID, value = Dist.CLIENT)
    public static class ExampleKey {
        @SubscribeEvent
        public static void onKey(ClientTickEvent.Post event) {
            while (ExampleModKeyMappings.EXAMPLE_ACTION.get().consumeClick()) {
                PacketDistributor.sendToServer(new ExampleRequestPacket(0));
            }
        }
    }
}
