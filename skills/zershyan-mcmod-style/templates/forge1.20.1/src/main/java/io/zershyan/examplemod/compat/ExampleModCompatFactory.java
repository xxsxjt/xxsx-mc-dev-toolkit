package io.zershyan.examplemod.compat;

import io.zershyan.examplemod.compat.examplelib.ExampleLibCompat;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.network.simple.SimpleChannel;

import java.util.LinkedHashSet;
import java.util.Set;

public class ExampleModCompatFactory {
    private static final Set<ICompatUtils> compatUtils = new LinkedHashSet<>();
    public static final ExampleLibCompat ExampleLib = addCompat(new ExampleLibCompat());

    private static <T extends ICompatUtils> T addCompat(T utils) {
        if (!compatUtils.add(utils)) {
            throw new IllegalStateException("兼容实现已添加");
        }
        return utils;
    }

    public static void register(IEventBus forgeBus, IEventBus modBus) {
        compatUtils.forEach(utils -> utils.initial(forgeBus, modBus));
    }

    public static void registerNetwork(SimpleChannel channel) {
        compatUtils.forEach(utils -> utils.initNetwork(channel));
    }
}
