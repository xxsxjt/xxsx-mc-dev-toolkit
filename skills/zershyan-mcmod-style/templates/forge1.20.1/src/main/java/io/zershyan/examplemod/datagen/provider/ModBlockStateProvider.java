package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModBlocks;
import net.minecraft.data.PackOutput;
import net.minecraftforge.client.model.generators.BlockStateProvider;
import net.minecraftforge.common.data.ExistingFileHelper;

public class ModBlockStateProvider extends BlockStateProvider {
    public ModBlockStateProvider(PackOutput output, ExistingFileHelper helper) {
        super(output, ExampleMod.MODID, helper);
    }

    @Override
    protected void registerStatesAndModels() {
        simpleBlockWithItem(ExampleModBlocks.EXAMPLE_BLOCK.get(), cubeAll(ExampleModBlocks.EXAMPLE_BLOCK.get()));
        simpleBlockWithItem(ExampleModBlocks.EXAMPLE_CUSTOM_BLOCK.get(), cubeAll(ExampleModBlocks.EXAMPLE_CUSTOM_BLOCK.get()));
    }
}
