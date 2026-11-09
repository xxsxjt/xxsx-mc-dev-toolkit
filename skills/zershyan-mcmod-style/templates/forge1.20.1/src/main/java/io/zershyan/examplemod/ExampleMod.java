package io.zershyan.examplemod;

import io.zershyan.examplemod.compat.ExampleModCompatFactory;
import io.zershyan.examplemod.registry.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Mod(ExampleMod.MODID)
public class ExampleMod {
    public static final String MODID = "examplemod";
    public static final Logger LOGGER = LoggerFactory.getLogger(ExampleMod.class);

    public ExampleMod() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        IEventBus forgeBus = MinecraftForge.EVENT_BUS;

        ExampleModSounds.doRegister(modBus);
        ExampleModItems.doRegister(modBus);
        ExampleModBlocks.doRegister(modBus);
        ExampleModBlockEntityTypes.doRegister(modBus);
        ExampleModEntities.doRegister(modBus);
        ExampleModAttributes.doRegister(modBus);
        ExampleModCreativeTab.doRegister(modBus);
        ExampleModAttachments.doRegister(modBus);
        ExampleModRegistries.doRegister(modBus);
        ExampleModCustomRegistries.doRegister(modBus);
        ExampleModPackets.doRegister();
        ExampleModConfigs.doRegister();
        ExampleModCommands.doRegister(forgeBus, modBus);

        ExampleModCompatFactory.register(forgeBus, modBus);

        // Forge 1.20.1 没有 Dist 构造器参数，客户端注册必须经 DistExecutor 隔离
        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> {
            ExampleModOverlays.doRegister(modBus);
            ExampleModKeyMappings.doRegister(modBus);
            ExampleModEntityLayers.doRegister(modBus);
        });
    }

    public static ResourceLocation id(String path) {
        return new ResourceLocation(MODID, path);
    }
}
