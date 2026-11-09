package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.registry.config.ClientConfig;
import io.zershyan.examplemod.registry.config.CommonConfig;
import io.zershyan.examplemod.registry.config.ServerConfig;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.fml.loading.FMLLoader;
import net.neoforged.neoforge.client.gui.ConfigurationScreen;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;

public class ExampleModConfigs {

    public static void registerCommon(ModContainer container) {
        container.registerConfig(ModConfig.Type.COMMON, CommonConfig.SPEC);
        container.registerConfig(ModConfig.Type.SERVER, ServerConfig.SPEC);
    }

    public static void registerClient(ModContainer container) {
        container.registerConfig(ModConfig.Type.CLIENT, ClientConfig.SPEC);
        container.registerExtensionPoint(IConfigScreenFactory.class, ConfigurationScreen::new);
    }

    public static void doRegister(ModContainer container) {
        if (FMLLoader.getDist().isClient()) registerClient(container);
        registerCommon(container);
    }
}
