package io.zershyan.examplemod.compat;

import io.zershyan.examplemod.compat.examplelib.ExampleLibCompat;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

import java.util.HashSet;
import java.util.Set;

/** 兼容工厂：持有全部兼容实现并在主类统一触发 */
public class ExampleModCompatFactory {
    private static final Set<ICompatUtils> compatUtils = new HashSet<>();

    public static final ExampleLibCompat ExampleLib = addCompat(new ExampleLibCompat());

    private static <T extends ICompatUtils> T addCompat(T utils) {
        if (compatUtils.add(utils)) {
            return utils;
        } else throw new IllegalStateException("CompatUtils already added.");
    }

    public static void register(IEventBus forgeEventBus, IEventBus modEventBus) {
        compatUtils.forEach(compatUtils -> compatUtils.initial(forgeEventBus, modEventBus));
    }

    public static void registerNetwork(PayloadRegistrar registrar) {
        compatUtils.forEach(compatUtils -> compatUtils.initNetwork(registrar));
    }
}
