package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.custom_registry.SimpleExampleStyle;
import io.zershyan.examplemod.registry.custom_registry.builder.IExampleStyle;
import net.minecraft.core.Holder;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredRegister;

/** 自定义注册表的注册项入口 */
public class ExampleModCustomRegistries {
    public static final DeferredRegister<IExampleStyle> REGISTER =
            DeferredRegister.create(ExampleModRegistries.CUSTOM_REGISTRY, ExampleMod.MODID);

    public static final Holder<IExampleStyle> SIMPLE = REGISTER.register("simple", SimpleExampleStyle::new);

    public static void doRegister(IEventBus modBus) {
        REGISTER.register(modBus);
    }
}