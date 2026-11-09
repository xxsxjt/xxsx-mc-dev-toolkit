package io.zershyan.examplemod.registry.config;

import io.zershyan.examplemod.datagen.lang.ExampleModConfigLang;
import net.minecraftforge.common.ForgeConfigSpec;

public class ClientConfig {
    private static final ForgeConfigSpec.Builder BUILDER = new ForgeConfigSpec.Builder();
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.BooleanValue SHOW_OVERLAY;

    static {
        SHOW_OVERLAY = BUILDER.comment("是否显示示例 HUD 叠层")
                .translation(ExampleModConfigLang.ShowOverlay.key())
                .define(ExampleModConfigLang.ShowOverlay.name(), true);

        SPEC = BUILDER.build();
    }
}
