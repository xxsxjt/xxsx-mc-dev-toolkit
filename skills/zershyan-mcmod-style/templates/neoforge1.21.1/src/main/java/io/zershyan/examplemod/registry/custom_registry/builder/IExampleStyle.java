package io.zershyan.examplemod.registry.custom_registry.builder;

import io.zershyan.examplemod.datagen.lang.ExampleModLang;
import io.zershyan.examplemod.registry.ExampleModRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;

/** 自定义注册项的类型接口 */
@FunctionalInterface
public interface IExampleStyle {

    /** 示例：把输入文本转换为该风格 */
    @Nullable String convert(String input);

    default @Nullable String getDisplayName() {
        return null;
    }

    default Component getDescription() {
        String displayName = getDisplayName();
        if (displayName == null) {
            ResourceLocation keyOrNull = ExampleModRegistries.CUSTOM_REGISTRY.getKeyOrNull(this);
            if (keyOrNull == null) return Component.empty();
            return Component.translatable(ExampleModLang.getCustomRegistryDesc(keyOrNull));
        } else return Component.literal(displayName);
    }
}