package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.attachment.ExampleStatusData;
import io.zershyan.forgeattachment.attachment.AttachmentType;
import io.zershyan.forgeattachment.registry.ForgeAttachmentRegistries;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/**
 * 附件注册入口。
 *
 * <p>Forge 1.20.1 没有原生的 AttachmentType，由其依赖 forgeattachment 提供等价能力。
 */
public class ExampleModAttachments {
    public static final DeferredRegister<AttachmentType<?>> REGISTER =
            DeferredRegister.create(ForgeAttachmentRegistries.ATTACHMENT_TYPES_KEY, ExampleMod.MODID);

    public static final RegistryObject<AttachmentType<ExampleStatusData>> EXAMPLE_STATUS =
            REGISTER.register("example_status", ExampleStatusData::createType);

    public static void doRegister(IEventBus eventBus) {
        REGISTER.register(eventBus);
    }
}
