package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModItems;
import io.zershyan.examplemod.util.data.ModTagKey;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.data.tags.ItemTagsProvider;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.common.data.ExistingFileHelper;

import java.util.concurrent.CompletableFuture;

public class ModItemTagProvider extends ItemTagsProvider {
    public ModItemTagProvider(PackOutput output, CompletableFuture<HolderLookup.Provider> lookup,
                              CompletableFuture<TagLookup<Block>> blockTags, ExistingFileHelper helper) {
        super(output, lookup, blockTags, ExampleMod.MODID, helper);
    }

    @Override
    protected void addTags(HolderLookup.Provider provider) {
        copy(ModTagKey.Blocks.EXAMPLE_BLOCKS, ModTagKey.Items.EXAMPLE_ITEMS);
        tag(ModTagKey.Items.EXAMPLE_ITEMS).add(
                ExampleModItems.EXAMPLE_ITEM.get(), ExampleModItems.EXAMPLE_CUSTOM_ITEM.get());
    }
}
