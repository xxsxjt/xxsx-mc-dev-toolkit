package io.zershyan.examplemod.registry.config;

import io.zershyan.examplemod.datagen.lang.ExampleModConfigLang;
import net.minecraftforge.common.ForgeConfigSpec;

public class CommonConfig {
    private static final ForgeConfigSpec.Builder BUILDER = new ForgeConfigSpec.Builder();
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.BooleanValue ENABLE_FEATURE;

    static {
        ENABLE_FEATURE = BUILDER.comment("是否启用示例功能")
                .translation(ExampleModConfigLang.EnableFeature.key())
                .define(ExampleModConfigLang.EnableFeature.name(), true);

        SPEC = BUILDER.build();
    }
}
