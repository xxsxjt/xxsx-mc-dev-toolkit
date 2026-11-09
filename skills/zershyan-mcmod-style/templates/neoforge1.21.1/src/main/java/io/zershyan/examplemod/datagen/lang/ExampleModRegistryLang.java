package io.zershyan.examplemod.datagen.lang;

import io.zershyan.examplemod.registry.*;
import io.zershyan.examplemod.registry.custom_registry.builder.IExampleStyle;
import net.minecraft.core.Holder;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;

public class ExampleModRegistryLang extends ExampleModLang {

    private void entryItem(DeferredItem<?> item, String enUs, String zhCn) {
        addFinalEntry(item.asItem(), enUs, zhCn);
    }

    private void entryBlock(DeferredBlock<?> block, String enUs, String zhCn) {
        addFinalEntry(block.get(), enUs, zhCn);
    }

    private void entrySound(Holder<SoundEvent> sound, String enUs, String zhCn) {
        addFinalEntry(getSoundDesc(sound.value().getLocation()), enUs, zhCn);
    }

    /** 自定义注册项的键跟随其 ResourceLocation */
    private void entryCustomRegistry(Holder<IExampleStyle> style, String enUs, String zhCn) {
        style.unwrapKey().map(ResourceKey::location).map(ExampleModLang::getCustomRegistryDesc)
                .ifPresent(key -> addFinalEntry(key, enUs, zhCn));
    }

    private void entryAttribute(Holder<Attribute> attribute, String enUs, String zhCn) {
        attribute.unwrapKey().map(ResourceKey::location).map(ExampleModLang::getAttributeDesc)
                .ifPresent(key -> addFinalEntry(key, enUs, zhCn));
    }

    @Override
    protected void init() {
        entryItem(ExampleModItems.EXAMPLE_ITEM, "Example Item", "示例物品");
        entryItem(ExampleModItems.EXAMPLE_CUSTOM_ITEM, "Example Custom Item", "示例自定义物品");
        entryBlock(ExampleModBlocks.EXAMPLE_BLOCK, "Example Block", "示例方块");
        entryBlock(ExampleModBlocks.EXAMPLE_CUSTOM_BLOCK, "Example Custom Block", "示例自定义方块");
        entrySound(ExampleModSounds.EXAMPLE_SOUND, "Example Sound", "示例音效");
        entryAttribute(ExampleModAttributes.EXAMPLE_ABILITY, "Example Ability", "示例能力");
        entryCustomRegistry(ExampleModCustomRegistries.SIMPLE, "Simple Style", "简单风格");
    }
}
