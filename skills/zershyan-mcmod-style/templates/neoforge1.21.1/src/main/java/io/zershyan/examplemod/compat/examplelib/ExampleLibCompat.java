package io.zershyan.examplemod.compat.examplelib;

import io.zershyan.examplemod.compat.ICompatUtils;
import io.zershyan.examplemod.compat.examplelib.event.ExampleLibClientSetupEvent;
import io.zershyan.examplemod.compat.examplelib.event.ExampleLibCommonSetupEvent;
import io.zershyan.examplemod.compat.examplelib.util.ExampleLibUtils;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModList;

public class ExampleLibCompat implements ICompatUtils {
    public static final String MODID = "examplelib";

    @Override
    public boolean isModLoaded() {
        return ModList.get().isLoaded(MODID);
    }

    @Override
    public void addCommonListener(IEventBus forgeBus, IEventBus modBus) {
        modBus.register(ExampleLibCommonSetupEvent.class);
    }

    @Override
    public void addClientListener(IEventBus forgeBus, IEventBus modBus) {
        modBus.register(ExampleLibClientSetupEvent.class);
    }

    public String describe() {
        return testLoadedAndCall(ExampleLibUtils::describe, "");
    }
}
