package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.projectile.Snowball;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** 实体注册入口 */
public class ExampleModEntities {
    public static final DeferredRegister<EntityType<?>> REGISTRY =
            DeferredRegister.create(Registries.ENTITY_TYPE, ExampleMod.MODID);

    public static final DeferredHolder<EntityType<?>, EntityType<Snowball>> EXAMPLE_PROJECTILE =
            REGISTRY.register("example_projectile", () -> EntityType.Builder
                    .<Snowball>of(Snowball::new, MobCategory.MISC)
                    .sized(0.25F, 0.25F)
                    .build("example_projectile"));

    public static void doRegister(IEventBus modBus) {
        REGISTRY.register(modBus);
    }
}