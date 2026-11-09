package io.zershyan.examplemod.compat.examplelib.event;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.compat.examplelib.ExampleLibCompat;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;

/** 该兼容的通用侧事件；由 ExampleLibCompat.addCommonListener 注册 */
public final class ExampleLibCommonSetupEvent {

    private ExampleLibCommonSetupEvent() {
    }

    @SubscribeEvent
    public static void onCommonSetup(FMLCommonSetupEvent event) {
        if (!ExampleLibCompat.MODID.isEmpty()) {
            ExampleMod.LOGGER.debug("ExampleLib compat common setup done");
        }
    }
}
