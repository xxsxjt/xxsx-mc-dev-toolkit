package io.zershyan.examplemod.compat.examplelib.event;

import io.zershyan.examplemod.ExampleMod;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;

public class ExampleLibCommonSetupEvent {
    @SubscribeEvent
    public static void onCommonSetup(FMLCommonSetupEvent event) {
        ExampleMod.LOGGER.debug("ExampleLib compat common setup done");
    }
}
