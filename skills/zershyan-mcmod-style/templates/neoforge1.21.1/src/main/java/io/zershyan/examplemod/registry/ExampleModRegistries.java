package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.custom_registry.builder.IExampleStyle;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.NewRegistryEvent;
import net.neoforged.neoforge.registries.RegistryBuilder;

/**
 * 自定义注册表：先在此声明注册表本身，具体注册项由 ExampleModCustomRegistries 写入。
 */
public class ExampleModRegistries {
    public static final ResourceKey<Registry<IExampleStyle>> CUSTOM_REGISTRY_KEY =
            ResourceKey.createRegistryKey(ExampleMod.id("custom_registry"));

    public static final Registry<IExampleStyle> CUSTOM_REGISTRY =
            new RegistryBuilder<>(CUSTOM_REGISTRY_KEY).create();

    public static void createRegistry(NewRegistryEvent event) {
        event.register(CUSTOM_REGISTRY);
    }

    public static void doRegister(IEventBus modBus) {
        modBus.addListener(ExampleModRegistries::createRegistry);
    }
}