package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.registry.config.ClientConfig;
import io.zershyan.examplemod.registry.config.CommonConfig;
import io.zershyan.examplemod.registry.config.ServerConfig;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.loading.FMLLoader;

/**
 * 配置注册入口。
 *
 * <p>Forge 1.20.1 只有 COMMON / CLIENT / SERVER 三种，没有 Startup 配置。
 */
public class ExampleModConfigs {

    public static void registerCommon() {
        ModLoadingContext context = ModLoadingContext.get();
        context.registerConfig(ModConfig.Type.COMMON, CommonConfig.SPEC);
        context.registerConfig(ModConfig.Type.SERVER, ServerConfig.SPEC);
    }

    public static void registerClient() {
        ModLoadingContext.get().registerConfig(ModConfig.Type.CLIENT, ClientConfig.SPEC);
    }

    public static void doRegister() {
        if (FMLLoader.getDist().isClient()) registerClient();
        registerCommon();
    }
}
