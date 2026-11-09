package io.zershyan.examplemod.registry;

import com.mojang.blaze3d.platform.InputConstants;
import io.zershyan.examplemod.datagen.lang.ExampleModKeyLang;
import net.minecraft.client.KeyMapping;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.settings.KeyConflictContext;
import net.minecraftforge.common.util.Lazy;
import net.minecraftforge.eventbus.api.IEventBus;
import org.lwjgl.glfw.GLFW;

import java.util.ArrayList;
import java.util.List;

public class ExampleModKeyMappings {
    public static final List<Lazy<KeyMapping>> KEYS = new ArrayList<>();
    public static final Lazy<KeyMapping> EXAMPLE_ACTION = registerKeyMapping(ExampleModKeyLang.KeyAction, GLFW.GLFW_KEY_R);

    private static Lazy<KeyMapping> registerKeyMapping(String name, int keyValue) {
        Lazy<KeyMapping> mapping = Lazy.of(() -> new KeyMapping(
                name, KeyConflictContext.IN_GAME, InputConstants.Type.KEYSYM, keyValue, ExampleModKeyLang.KeyCategory));
        KEYS.add(mapping);
        return mapping;
    }

    public static void register(RegisterKeyMappingsEvent event) {
        KEYS.stream().map(Lazy::get).forEach(event::register);
    }

    public static void doRegister(IEventBus modBus) {
        modBus.addListener(ExampleModKeyMappings::register);
    }
}
