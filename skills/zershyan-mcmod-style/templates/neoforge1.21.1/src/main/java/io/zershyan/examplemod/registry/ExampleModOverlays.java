package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.registry.overlay.ExampleOverlay;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;

public class ExampleModOverlays {

    public static void registerOverlay(RegisterGuiLayersEvent event) {
        event.registerAboveAll(ExampleOverlay.ID, new ExampleOverlay());
    }

    public static void doRegister(IEventBus bus) {
        bus.addListener(ExampleModOverlays::registerOverlay);
    }
}
