package io.zershyan.examplemod.compat.examplelib.event;

import io.zershyan.examplemod.ExampleMod;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;

/** 该兼容的客户端侧事件；由 ExampleLibCompat.addClientListener 注册，只在客户端加载 */
public final class ExampleLibClientSetupEvent {

    private ExampleLibClientSetupEvent() {
    }

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        ExampleMod.LOGGER.debug("ExampleLib compat client setup done");
    }
}
