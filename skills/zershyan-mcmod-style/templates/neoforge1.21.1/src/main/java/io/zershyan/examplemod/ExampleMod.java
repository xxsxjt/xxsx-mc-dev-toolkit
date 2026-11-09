package io.zershyan.examplemod;

import io.zershyan.examplemod.compat.ExampleModCompatFactory;
import io.zershyan.examplemod.registry.*;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Mod(ExampleMod.MODID)
public class ExampleMod {
    public static final String MODID = "examplemod";
    public static final Logger LOGGER = LoggerFactory.getLogger(ExampleMod.class);

    public ExampleMod(IEventBus modEventBus, Dist dist, ModContainer modContainer) {
        IEventBus neoEventBus = NeoForge.EVENT_BUS;

        ExampleModSounds.doRegister(modEventBus);
        ExampleModItems.doRegister(modEventBus);
        ExampleModBlocks.doRegister(modEventBus);
        ExampleModBlockEntityTypes.doRegister(modEventBus);
        ExampleModEntities.doRegister(modEventBus);
        ExampleModAttributes.doRegister(modEventBus);
        ExampleModCreativeTab.doRegister(modEventBus);
        ExampleModDataComponents.doRegister(modEventBus);
        ExampleModAttachments.doRegister(modEventBus);
        ExampleModRegistries.doRegister(modEventBus);
        ExampleModCustomRegistries.doRegister(modEventBus);
        ExampleModPackets.doRegister(modEventBus);
        ExampleModConfigs.doRegister(modContainer);
        ExampleModCommands.doRegister(neoEventBus);

        //compat
        ExampleModCompatFactory.register(neoEventBus, modEventBus);

        if (dist.isClient()) {
            ExampleModOverlays.doRegister(modEventBus);
            ExampleModKeyMappings.doRegister(modEventBus);
            ExampleModEntityLayers.doRegister(modEventBus);
        }
    }

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MODID, path);
    }
}
