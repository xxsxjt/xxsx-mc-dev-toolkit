package io.zershyan.examplemod.handler.common;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModAttachments;
import io.zershyan.examplemod.registry.attachment.ExampleStatusData;
import io.zershyan.examplemod.registry.config.CommonConfig;
import io.zershyan.examplemod.registry.config.ServerConfig;
import io.zershyan.forgeattachment.attachment.IAttachmentHolder;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = ExampleMod.MODID)
public class PlayerStatusHandler {
    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !CommonConfig.ENABLE_FEATURE.get()) return;
        if (!(event.player instanceof ServerPlayer player) || !(player instanceof IAttachmentHolder holder)) return;
        ExampleStatusData data = holder.getData(ExampleModAttachments.EXAMPLE_STATUS.get());
        int value = Math.max(0, Math.min(data.getValue(), ServerConfig.MAX_VALUE.get()));
        if (value != data.getValue()) {
            data.setValue(value);
            holder.syncData(ExampleModAttachments.EXAMPLE_STATUS.get());
        }
    }
}
