package io.zershyan.examplemod.util;

import io.zershyan.examplemod.ExampleMod;
import net.minecraft.resources.ResourceLocation;

/** 通用工具 */
public final class ExampleUtil {

    private ExampleUtil() {
    }

    /** 构造本 mod 的 ResourceLocation，路径需为 lower_snake_case */
    public static ResourceLocation id(String path) {
        return ExampleMod.id(path);
    }
}
