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
import net.neoforged.neoforge.common.data.LanguageProvider;

public class ModLangProvider extends LanguageProvider {
    private static final String enUs = "en_us";
    private static final String zhCn = "zh_cn";
    private final String locale;

    public ModLangProvider(PackOutput output, String locale) {
        super(output, ExampleMod.MODID, locale);
        this.locale = locale;
    }

    public static ModLangProvider runZhCn(PackOutput output) {
        return new ModLangProvider(output, zhCn);
    }

    public static ModLangProvider runEnUs(PackOutput output) {
        return new ModLangProvider(output, enUs);
    }

    @Override
    protected void addTranslations() {
        switch (locale) {
            case enUs -> ExampleModLang.getAllLang().forEach(langEntity ->
                    addTranslation(langEntity.key(), langEntity.lang().enUs())
            );
            case zhCn -> ExampleModLang.getAllLang().forEach(langEntity ->
                    addTranslation(langEntity.key(), langEntity.lang().zhCn())
            );
        }
    }

    private <T> void addTranslation(T o, String desc) {
        switch (o) {
            case Item object -> add(object, desc);
            case Block object -> add(object, desc);
            case String object -> add(object, desc);
            case ItemStack object -> add(object.getItem(), desc);
            case MobEffect object -> add(object, desc);
            case EntityType<?> object -> add(object, desc);
            case TagKey<?> object -> add(object, desc);
            default -> {
                ExampleMod.LOGGER.error("Unknown object type: {}", o.getClass());
                add(o.toString(), desc);
            }
        }
    }
}
