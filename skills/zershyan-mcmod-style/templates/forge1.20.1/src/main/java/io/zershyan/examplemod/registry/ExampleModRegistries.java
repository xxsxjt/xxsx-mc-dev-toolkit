package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.custom_registry.builder.IExampleStyle;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.IForgeRegistry;
import net.minecraftforge.registries.NewRegistryEvent;
import net.minecraftforge.registries.RegistryBuilder;

import java.util.function.Supplier;

/**
 * 自定义注册表：先在此声明注册表本身，具体注册项由 ExampleModCustomRegistries 写入。
 */
public class ExampleModRegistries {
    public static final ResourceKey<Registry<IExampleStyle>> CUSTOM_REGISTRY_KEY =
            ResourceKey.createRegistryKey(ExampleMod.id("custom_registry"));

    private static Supplier<IForgeRegistry<IExampleStyle>> customRegistry;

    /** 仅在 {@link #doRegister(IEventBus)} 所挂的 {@link NewRegistryEvent} 触发后可用 */
    public static IForgeRegistry<IExampleStyle> customRegistry() {
        return customRegistry.get();
    }

    private static void createRegistries(NewRegistryEvent event) {
        customRegistry = event.create(new RegistryBuilder<IExampleStyle>()
                .setName(CUSTOM_REGISTRY_KEY.location()));
    }

    public static void doRegister(IEventBus modBus) {
        modBus.addListener(ExampleModRegistries::createRegistries);
    }
}
