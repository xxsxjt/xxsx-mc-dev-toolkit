package io.zershyan.examplemod.datagen;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.provider.*;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.DataGenerator;
import net.minecraft.data.PackOutput;
import net.minecraftforge.common.data.ExistingFileHelper;
import net.minecraftforge.data.event.GatherDataEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.concurrent.CompletableFuture;

@Mod.EventBusSubscriber(modid = ExampleMod.MODID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class DataGeneratorHandler {
    @SubscribeEvent
    public static void gatherData(GatherDataEvent event) {
        DataGenerator generator = event.getGenerator();
        PackOutput output = generator.getPackOutput();
        ExistingFileHelper helper = event.getExistingFileHelper();
        CompletableFuture<HolderLookup.Provider> lookup = event.getLookupProvider();

        ModBlockTagProvider blockTags = new ModBlockTagProvider(output, lookup, helper);
        generator.addProvider(event.includeServer(), blockTags);
        generator.addProvider(event.includeServer(), new ModItemTagProvider(output, lookup, blockTags.contentsGetter(), helper));
        generator.addProvider(event.includeServer(), new ModLootTableProvider(output));
        generator.addProvider(event.includeClient(), ModLangProvider.runEnUs(output));
        generator.addProvider(event.includeClient(), ModLangProvider.runZhCn(output));
        generator.addProvider(event.includeClient(), new ModItemModelProvider(output, helper));
        generator.addProvider(event.includeClient(), new ModBlockStateProvider(output, helper));
        generator.addProvider(event.includeClient() || event.includeServer(), new PackMetadataProvider(output));
        // 放入 assets/<modid>/sounds/example_sound.ogg 后再启用声音定义生成。
        // generator.addProvider(event.includeClient(), new ModSoundProvider(output, helper));
    }
}
