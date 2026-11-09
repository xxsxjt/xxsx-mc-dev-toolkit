package io.zershyan.examplemod.datagen.util;

import io.zershyan.examplemod.ExampleMod;

/** 配置项语言键：<modid>.configuration.<name> */
public record ConfigLangEntry(String name) {
    public String key() {
        return ExampleMod.MODID + ".configuration." + name;
    }
}
