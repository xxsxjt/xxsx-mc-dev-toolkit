package io.zershyan.examplemod.compat.examplelib.util;

import io.zershyan.examplemod.compat.examplelib.ExampleLibCompat;

/** 第三方 API 的调用收在这里，由兼容实现先检查依赖。 */
public class ExampleLibUtils {
    public static String describe() {
        return ExampleLibCompat.MODID;
    }
}
