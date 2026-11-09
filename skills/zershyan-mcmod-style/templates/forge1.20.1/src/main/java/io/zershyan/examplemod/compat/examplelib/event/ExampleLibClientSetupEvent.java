package io.zershyan.examplemod.compat.examplelib.event;

import io.zershyan.examplemod.ExampleMod;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

public class ExampleLibClientSetupEvent {
    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        ExampleMod.LOGGER.debug("ExampleLib compat client setup done");
    }
}
