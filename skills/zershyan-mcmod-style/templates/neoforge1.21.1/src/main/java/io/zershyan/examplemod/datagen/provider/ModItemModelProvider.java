package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModItems;
import net.minecraft.data.PackOutput;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.client.model.generators.ItemModelProvider;
import net.neoforged.neoforge.common.data.ExistingFileHelper;
import net.neoforged.neoforge.registries.DeferredHolder;

import java.util.LinkedHashSet;
import java.util.Set;

public class ModItemModelProvider extends ItemModelProvider {
    public ModItemModelProvider(PackOutput output, ExistingFileHelper existingFileHelper) {
        super(output, ExampleMod.MODID, existingFileHelper);
    }

    @Override
    protected void registerModels() {
        Set<DeferredHolder<Item, ? extends Item>> items = new LinkedHashSet<>();
        items.addAll(ExampleModItems.REGISTER.getEntries());
        items.stream().map(DeferredHolder::get).forEach(this::basicItem);
    }
}
