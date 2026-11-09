package io.zershyan.examplemod.datagen;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.provider.*;
import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.common.data.ExistingFileHelper;
import net.neoforged.neoforge.data.event.GatherDataEvent;

import java.util.concurrent.CompletableFuture;

@EventBusSubscriber(modid = ExampleMod.MODID)
public class DataGeneratorHandler {
    @SubscribeEvent
    public static void gatherData(GatherDataEvent event) {
        ExistingFileHelper helper = event.getExistingFileHelper();
        PackOutput packOutput = event.getGenerator().getPackOutput();
        CompletableFuture<HolderLookup.Provider> lookup = event.getLookupProvider();

        ModBlockTagProvider blockTags = new ModBlockTagProvider(packOutput, lookup, helper);
        event.addProvider(blockTags);
        event.addProvider(new ModItemTagProvider(packOutput, lookup, blockTags.contentsGetter(), helper));
        event.createProvider(ModLangProvider::runEnUs);
        event.createProvider(ModLangProvider::runZhCn);
        event.createProvider(ModLootTableProvider::new);
        event.createProvider(PackMetadataProvider::new);
        // ModSoundProvider 需要 assets/<modid>/sounds/ 下已存在对应 ogg 文件，
        // 否则 SoundDefinitionsProvider 校验会失败。放入音频后再启用这一行。
        // event.addProvider(new ModSoundProvider(packOutput, helper));
        event.addProvider(new ModItemModelProvider(packOutput, helper));
        event.addProvider(new ModBlockStateProvider(packOutput, helper));
    }
}
