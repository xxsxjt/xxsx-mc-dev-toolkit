package io.zershyan.examplemod.registry.config;

import io.zershyan.examplemod.datagen.lang.ExampleModConfigLang;
import net.minecraftforge.common.ForgeConfigSpec;

public class ServerConfig {
    private static final ForgeConfigSpec.Builder BUILDER = new ForgeConfigSpec.Builder();
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.IntValue MAX_VALUE;

    static {
        MAX_VALUE = BUILDER.comment("示例数值上限")
                .translation(ExampleModConfigLang.MaxValue.key())
                .defineInRange(ExampleModConfigLang.MaxValue.name(), 100, 0, 10000);

        SPEC = BUILDER.build();
    }
}
