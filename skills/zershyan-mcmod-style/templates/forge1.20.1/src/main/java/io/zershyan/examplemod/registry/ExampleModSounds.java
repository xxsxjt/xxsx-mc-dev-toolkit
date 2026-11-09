package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;

public class ExampleModSounds {
    public static final DeferredRegister<SoundEvent> REGISTRY =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, ExampleMod.MODID);

    public static final List<RegistryObject<SoundEvent>> SOUNDS = new ArrayList<>();

    public static final RegistryObject<SoundEvent> EXAMPLE_SOUND = registerSoundEvent("example_sound");

    private static RegistryObject<SoundEvent> registerSoundEvent(String name) {
        RegistryObject<SoundEvent> soundEvent = REGISTRY.register(name, () ->
                SoundEvent.createVariableRangeEvent(ExampleMod.id(name)));
        SOUNDS.add(soundEvent);
        return soundEvent;
    }

    public static void doRegister(IEventBus eventBus) {
        REGISTRY.register(eventBus);
    }
}
