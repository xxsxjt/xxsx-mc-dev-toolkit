package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.attachment.ExampleStatusData;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

import java.util.function.Supplier;

public class ExampleModAttachments {
    public static final DeferredRegister<AttachmentType<?>> REGISTER =
            DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, ExampleMod.MODID);

    public static final Supplier<AttachmentType<ExampleStatusData>> EXAMPLE_STATUS = REGISTER.register("example_status", () -> AttachmentType
            .<ExampleStatusData>builder(() -> new ExampleStatusData())
            .serialize(ExampleStatusData.CODEC)
            .sync(ExampleStatusData.STREAM_CODEC)
            .copyOnDeath()
            .build());

    public static void doRegister(IEventBus eventBus) {
        REGISTER.register(eventBus);
    }
}
