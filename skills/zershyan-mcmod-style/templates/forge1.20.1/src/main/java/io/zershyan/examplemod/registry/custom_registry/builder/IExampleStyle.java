package io.zershyan.examplemod.registry.custom_registry.builder;

import io.zershyan.examplemod.datagen.lang.ExampleModLang;
import io.zershyan.examplemod.registry.ExampleModRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;

@FunctionalInterface
public interface IExampleStyle {
    @Nullable String convert(String input);

    default @Nullable String getDisplayName() {
        return null;
    }

    default Component getDescription() {
        String displayName = getDisplayName();
        if (displayName != null) {
            return Component.literal(displayName);
        }
        ResourceLocation key = ExampleModRegistries.customRegistry().getKey(this);
        return key == null ? Component.empty() : Component.translatable(ExampleModLang.getCustomRegistryDesc(key));
    }
}
