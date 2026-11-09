package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.custom_registry.SimpleExampleStyle;
import io.zershyan.examplemod.registry.custom_registry.builder.IExampleStyle;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/** 自定义注册表的注册项入口 */
public class ExampleModCustomRegistries {
    public static final DeferredRegister<IExampleStyle> REGISTER =
            DeferredRegister.create(ExampleModRegistries.CUSTOM_REGISTRY_KEY, ExampleMod.MODID);

    public static final RegistryObject<IExampleStyle> SIMPLE =
            REGISTER.register("simple", SimpleExampleStyle::new);

    public static void doRegister(IEventBus modBus) {
        REGISTER.register(modBus);
    }
}
