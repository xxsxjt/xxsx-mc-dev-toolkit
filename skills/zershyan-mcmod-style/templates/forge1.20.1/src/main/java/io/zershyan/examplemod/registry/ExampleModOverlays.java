package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.registry.overlay.ExampleOverlay;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.eventbus.api.IEventBus;

public class ExampleModOverlays {

    public static void registerOverlay(RegisterGuiOverlaysEvent event) {
        event.registerAboveAll(ExampleOverlay.ID, new ExampleOverlay());
    }

    public static void doRegister(IEventBus bus) {
        bus.addListener(ExampleModOverlays::registerOverlay);
    }
}
