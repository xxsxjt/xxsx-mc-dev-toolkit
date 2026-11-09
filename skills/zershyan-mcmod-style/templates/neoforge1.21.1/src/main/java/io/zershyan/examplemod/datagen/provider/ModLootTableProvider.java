package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.registry.ExampleModBlocks;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.data.loot.BlockLootSubProvider;
import net.minecraft.data.loot.LootTableProvider;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.neoforged.neoforge.registries.DeferredBlock;
import org.jetbrains.annotations.NotNull;

import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

public class ModLootTableProvider extends LootTableProvider {
    public ModLootTableProvider(PackOutput output, CompletableFuture<HolderLookup.Provider> lookupProvider) {
        super(output, Set.of(), List.of(new SubProviderEntry(
                ModBlockLootSubProvider::new, LootContextParamSets.BLOCK
        )), lookupProvider);
    }

    private static class ModBlockLootSubProvider extends BlockLootSubProvider {
        protected ModBlockLootSubProvider(HolderLookup.Provider provider) {
            super(Set.of(), FeatureFlags.REGISTRY.allFlags(), provider);
        }

        @Override
        protected void generate() {
            dropSelf(ExampleModBlocks.EXAMPLE_BLOCK.get());
            dropSelf(ExampleModBlocks.EXAMPLE_CUSTOM_BLOCK.get());
        }

        @Override
        protected @NotNull Iterable<Block> getKnownBlocks() {
            return List.of(ExampleModBlocks.EXAMPLE_BLOCK, ExampleModBlocks.EXAMPLE_CUSTOM_BLOCK).stream()
                    .map(DeferredBlock::get).collect(Collectors.toSet());
        }
    }
}
