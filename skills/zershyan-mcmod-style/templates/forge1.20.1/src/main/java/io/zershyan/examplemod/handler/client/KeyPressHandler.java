package io.zershyan.examplemod.handler.client;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModKeyMappings;
import io.zershyan.examplemod.registry.ExampleModPackets;
import io.zershyan.examplemod.registry.packet.ExampleRequestPacket;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = ExampleMod.MODID, value = Dist.CLIENT)
public class KeyPressHandler {
    @SubscribeEvent
    public static void onKey(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft minecraft = Minecraft.getInstance();
        while (ExampleModKeyMappings.EXAMPLE_ACTION.get().consumeClick()) {
            if (minecraft.player != null && minecraft.getConnection() != null) {
                ExampleModPackets.INSTANCE.sendToServer(new ExampleRequestPacket(0));
            }
        }
    }
}
