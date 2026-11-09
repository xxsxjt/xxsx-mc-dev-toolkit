package io.zershyan.examplemod.registry.custom_registry;

import io.zershyan.examplemod.registry.custom_registry.builder.IExampleStyle;
import org.jetbrains.annotations.NotNull;

/** 自定义注册项的实现示例 */
public class SimpleExampleStyle implements IExampleStyle {

    @Override
    public @NotNull String convert(String input) {
        return input.toUpperCase();
    }
}