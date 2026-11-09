package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.lang.ExampleModLang;
import net.minecraft.data.PackOutput;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.common.data.LanguageProvider;

public class ModLangProvider extends LanguageProvider {
    private final String locale;

    public ModLangProvider(PackOutput output, String locale) {
        super(output, ExampleMod.MODID, locale);
        this.locale = locale;
    }

    public static ModLangProvider runEnUs(PackOutput output) {
        return new ModLangProvider(output, "en_us");
    }

    public static ModLangProvider runZhCn(PackOutput output) {
        return new ModLangProvider(output, "zh_cn");
    }

    @Override
    protected void addTranslations() {
        ExampleModLang.getAllLang().forEach(entry -> addTranslation(entry.key(),
                "zh_cn".equals(locale) ? entry.lang().zhCn() : entry.lang().enUs()));
    }

    private void addTranslation(Object key, String text) {
        if (key instanceof Item item) add(item, text);
        else if (key instanceof Block block) add(block, text);
        else if (key instanceof String string) add(string, text);
        else if (key instanceof ItemStack stack) add(stack.getItem(), text);
        else if (key instanceof MobEffect effect) add(effect, text);
        else if (key instanceof EntityType<?> entity) add(entity, text);
        else if (key instanceof TagKey<?> tag) add(tag.location().toLanguageKey("tag"), text);
        else throw new IllegalArgumentException("不支持的语言键类型：" + key);
    }
}
