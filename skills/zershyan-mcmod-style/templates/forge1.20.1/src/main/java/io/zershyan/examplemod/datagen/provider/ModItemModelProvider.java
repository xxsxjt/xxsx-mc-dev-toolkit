package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModItems;
import net.minecraft.data.PackOutput;
import net.minecraftforge.client.model.generators.ItemModelProvider;
import net.minecraftforge.common.data.ExistingFileHelper;

public class ModItemModelProvider extends ItemModelProvider {
    public ModItemModelProvider(PackOutput output, ExistingFileHelper helper) {
        super(output, ExampleMod.MODID, helper);
    }

    @Override
    protected void registerModels() {
        ExampleModItems.REGISTER.getEntries().forEach(item -> basicItem(item.get()));
    }
}
