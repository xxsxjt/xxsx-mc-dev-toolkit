package io.zershyan.examplemod.datagen.provider;

import io.zershyan.examplemod.datagen.lang.ExampleModKeyLang;
import net.minecraft.DetectedVersion;
import net.minecraft.data.PackOutput;
import net.minecraft.data.metadata.PackMetadataGenerator;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.metadata.pack.PackMetadataSection;

public class PackMetadataProvider extends PackMetadataGenerator {
    public PackMetadataProvider(PackOutput pOutput) {
        super(pOutput);
        add(PackMetadataSection.TYPE, new PackMetadataSection(
                ExampleModKeyLang.Resource,
                DetectedVersion.BUILT_IN.getPackVersion(PackType.SERVER_DATA)
        ));
    }
}
