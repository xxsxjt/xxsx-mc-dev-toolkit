package io.zershyan.examplemod.datagen.lang;

import io.zershyan.examplemod.registry.*;
import io.zershyan.examplemod.registry.custom_registry.builder.IExampleStyle;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.registries.RegistryObject;

public class ExampleModRegistryLang extends ExampleModLang {
    private void entryItem(RegistryObject<? extends Item> item, String enUs, String zhCn) {
        addFinalEntry(item.get(), enUs, zhCn);
    }

    private void entryBlock(RegistryObject<? extends Block> block, String enUs, String zhCn) {
        addFinalEntry(block.get(), enUs, zhCn);
    }

    private void entrySound(RegistryObject<SoundEvent> sound, String enUs, String zhCn) {
        addFinalEntry(getSoundDesc(sound.getId()), enUs, zhCn);
    }

    private void entryAttribute(RegistryObject<Attribute> attribute, String enUs, String zhCn) {
        addFinalEntry(getAttributeDesc(attribute.getId()), enUs, zhCn);
    }

    private void entryCustomRegistry(RegistryObject<IExampleStyle> style, String enUs, String zhCn) {
        addFinalEntry(getCustomRegistryDesc(style.getId()), enUs, zhCn);
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
