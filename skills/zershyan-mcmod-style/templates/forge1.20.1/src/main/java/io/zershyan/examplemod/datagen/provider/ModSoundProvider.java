package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.lang.ExampleModLang;
import io.zershyan.examplemod.registry.ExampleModSounds;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.common.data.ExistingFileHelper;
import net.minecraftforge.common.data.SoundDefinitionsProvider;

public class ModSoundProvider extends SoundDefinitionsProvider {
    public ModSoundProvider(PackOutput output, ExistingFileHelper helper) {
        super(output, ExampleMod.MODID, helper);
    }

    @Override
    public void registerSounds() {
        ExampleModSounds.SOUNDS.forEach(sound -> {
            SoundEvent event = sound.get();
            ResourceLocation name = event.getLocation();
            add(event, definition().with(sound(name)).subtitle(ExampleModLang.getSoundDesc(name)));
        });
    }
}
