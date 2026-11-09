package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.block.ExampleBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ExampleModBlocks {
    public static final DeferredRegister<Block> REGISTRY =
            DeferredRegister.create(ForgeRegistries.BLOCKS, ExampleMod.MODID);

    public static final RegistryObject<Block> EXAMPLE_BLOCK = REGISTRY.register("example_block", () ->
            new Block(BlockBehaviour.Properties.of()
                    .strength(1.0F)
                    .sound(SoundType.STONE)));

    public static final RegistryObject<Block> EXAMPLE_CUSTOM_BLOCK = REGISTRY.register("example_custom_block", () ->
            new ExampleBlock(BlockBehaviour.Properties.of()
                    .strength(1.0F)
                    .sound(SoundType.STONE)));

    public static void doRegister(IEventBus modBus) {
        REGISTRY.register(modBus);
    }
}
