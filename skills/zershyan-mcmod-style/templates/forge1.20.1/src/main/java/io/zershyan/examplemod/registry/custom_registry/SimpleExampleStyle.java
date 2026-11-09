package io.zershyan.examplemod.registry.custom_registry;

import io.zershyan.examplemod.registry.custom_registry.builder.IExampleStyle;

import java.util.Locale;

public class SimpleExampleStyle implements IExampleStyle {
    @Override
    public String convert(String input) {
        return input.toUpperCase(Locale.ROOT);
    }
}
