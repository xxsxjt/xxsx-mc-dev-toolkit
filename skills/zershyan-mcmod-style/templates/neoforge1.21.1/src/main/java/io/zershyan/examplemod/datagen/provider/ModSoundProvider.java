package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.lang.ExampleModLang;
import io.zershyan.examplemod.registry.ExampleModSounds;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.neoforge.common.data.ExistingFileHelper;
import net.neoforged.neoforge.common.data.SoundDefinitionsProvider;

public class ModSoundProvider extends SoundDefinitionsProvider {
    public ModSoundProvider(PackOutput output, ExistingFileHelper helper) {
        super(output, ExampleMod.MODID, helper);
    }

    @Override
    public void registerSounds() {
        ExampleModSounds.SOUNDS.forEach(sound -> {
            SoundEvent soundEvent = sound.value();
            ResourceLocation name = soundEvent.getLocation();
            String translatableKey = ExampleModLang.getSoundDesc(name);
            add(soundEvent, definition().with(sound(name)).subtitle(translatableKey));
        });
    }
}
