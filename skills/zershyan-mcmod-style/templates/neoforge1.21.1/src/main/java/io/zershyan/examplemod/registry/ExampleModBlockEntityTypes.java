package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.block.entity.ExampleBlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ExampleModBlockEntityTypes {
    public static final DeferredRegister<BlockEntityType<?>> REGISTRY =
            DeferredRegister.create(net.minecraft.core.registries.Registries.BLOCK_ENTITY_TYPE, ExampleMod.MODID);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<ExampleBlockEntity>> EXAMPLE_BLOCK_ENTITY =
            REGISTRY.register("example_block_entity", () -> BlockEntityType.Builder
                    .of(ExampleBlockEntity::new, ExampleModBlocks.EXAMPLE_CUSTOM_BLOCK.get())
                    .build(null));

    public static void doRegister(IEventBus eventBus) {
        REGISTRY.register(eventBus);
    }
}
