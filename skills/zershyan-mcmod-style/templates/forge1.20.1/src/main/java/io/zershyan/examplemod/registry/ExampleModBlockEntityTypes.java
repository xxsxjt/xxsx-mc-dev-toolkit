package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.block.entity.ExampleBlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ExampleModBlockEntityTypes {
    public static final DeferredRegister<BlockEntityType<?>> REGISTRY =
            DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES, ExampleMod.MODID);

    public static final RegistryObject<BlockEntityType<ExampleBlockEntity>> EXAMPLE_BLOCK_ENTITY =
            REGISTRY.register("example_block_entity", () -> BlockEntityType.Builder
                    .of(ExampleBlockEntity::new, ExampleModBlocks.EXAMPLE_CUSTOM_BLOCK.get())
                    .build(null));

    public static void doRegister(IEventBus eventBus) {
        REGISTRY.register(eventBus);
    }
}
