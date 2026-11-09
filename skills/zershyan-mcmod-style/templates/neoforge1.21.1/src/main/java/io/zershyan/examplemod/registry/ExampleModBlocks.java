package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.block.ExampleBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ExampleModBlocks {
    public static final DeferredRegister.Blocks REGISTRY = DeferredRegister.createBlocks(ExampleMod.MODID);

    public static final DeferredBlock<Block> EXAMPLE_BLOCK = REGISTRY.register("example_block", () ->
            new Block(BlockBehaviour.Properties.of()
                    .strength(1.0F)
                    .sound(SoundType.STONE)));

    public static final DeferredBlock<Block> EXAMPLE_CUSTOM_BLOCK = REGISTRY.register("example_custom_block", () ->
            new ExampleBlock(BlockBehaviour.Properties.of()
                    .strength(1.0F)
                    .sound(SoundType.STONE)));

    public static void doRegister(IEventBus modBus) {
        REGISTRY.register(modBus);
    }
}
