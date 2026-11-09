package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.ArrayList;
import java.util.List;

public class ExampleModSounds {
    public static final DeferredRegister<SoundEvent> REGISTRY = DeferredRegister.create(Registries.SOUND_EVENT, ExampleMod.MODID);

    public static final List<Holder<SoundEvent>> SOUNDS = new ArrayList<>();

    public static final Holder<SoundEvent> EXAMPLE_SOUND = registerSoundEvent("example_sound");

    private static Holder<SoundEvent> registerSoundEvent(String name) {
        Holder<SoundEvent> soundEvent = REGISTRY.register(name, () ->
                SoundEvent.createVariableRangeEvent(ExampleMod.id(name)));
        SOUNDS.add(soundEvent);
        return soundEvent;
    }

    public static void doRegister(IEventBus eventBus) {
        REGISTRY.register(eventBus);
    }
}
