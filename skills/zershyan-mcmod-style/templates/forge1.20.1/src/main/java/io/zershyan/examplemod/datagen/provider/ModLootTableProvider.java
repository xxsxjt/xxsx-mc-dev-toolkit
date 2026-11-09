package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.registry.ExampleModBlocks;
import net.minecraft.data.PackOutput;
import net.minecraft.data.loot.BlockLootSubProvider;
import net.minecraft.data.loot.LootTableProvider;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraftforge.registries.RegistryObject;

import java.util.List;
import java.util.Set;

public class ModLootTableProvider extends LootTableProvider {
    public ModLootTableProvider(PackOutput output) {
        super(output, Set.of(), List.of(new SubProviderEntry(ModBlockLootSubProvider::new, LootContextParamSets.BLOCK)));
    }

    private static class ModBlockLootSubProvider extends BlockLootSubProvider {
        private ModBlockLootSubProvider() {
            super(Set.of(), FeatureFlags.REGISTRY.allFlags());
        }

        @Override
        protected void generate() {
            getKnownBlocks().forEach(this::dropSelf);
        }

        @Override
        protected Iterable<Block> getKnownBlocks() {
            return ExampleModBlocks.REGISTRY.getEntries().stream().map(RegistryObject::get).toList();
        }
    }
}
