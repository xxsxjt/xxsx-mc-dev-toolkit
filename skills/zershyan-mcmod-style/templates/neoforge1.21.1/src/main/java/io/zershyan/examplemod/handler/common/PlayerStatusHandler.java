package io.zershyan.examplemod.handler.common;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModAttachments;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

@EventBusSubscriber(modid = ExampleMod.MODID)
public final class PlayerStatusHandler {

    private PlayerStatusHandler() {
    }

    @SubscribeEvent
    public static void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        int value = player.getData(ExampleModAttachments.EXAMPLE_STATUS.get()).getValue();
        if (value < 0) {
            player.getData(ExampleModAttachments.EXAMPLE_STATUS.get()).setValue(0);
        }
    }

    @SubscribeEvent
    public static void onPlayerClone(PlayerEvent.Clone event) {
        if (!event.isWasDeath()) return;
        event.getEntity().getData(ExampleModAttachments.EXAMPLE_STATUS.get())
                .setValue(event.getOriginal().getData(ExampleModAttachments.EXAMPLE_STATUS.get()).getValue());
    }
}
