package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModBlocks;
import io.zershyan.examplemod.util.data.ModTagKey;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.tags.BlockTags;
import net.minecraftforge.common.data.BlockTagsProvider;
import net.minecraftforge.common.data.ExistingFileHelper;

import java.util.concurrent.CompletableFuture;

public class ModBlockTagProvider extends BlockTagsProvider {
    public ModBlockTagProvider(PackOutput output, CompletableFuture<HolderLookup.Provider> lookup, ExistingFileHelper helper) {
        super(output, lookup, ExampleMod.MODID, helper);
    }

    @Override
    protected void addTags(HolderLookup.Provider provider) {
        tag(ModTagKey.Blocks.EXAMPLE_BLOCKS).add(
                ExampleModBlocks.EXAMPLE_BLOCK.get(), ExampleModBlocks.EXAMPLE_CUSTOM_BLOCK.get());
        tag(BlockTags.MINEABLE_WITH_PICKAXE).addTag(ModTagKey.Blocks.EXAMPLE_BLOCKS);
    }
}
