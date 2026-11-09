package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.projectile.Snowball;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** 实体注册入口 */
public class ExampleModEntities {
    public static final DeferredRegister<EntityType<?>> REGISTRY =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, ExampleMod.MODID);

    public static final RegistryObject<EntityType<Snowball>> EXAMPLE_PROJECTILE =
            REGISTRY.register("example_projectile", () -> EntityType.Builder
                    .<Snowball>of(Snowball::new, MobCategory.MISC)
                    .sized(0.25F, 0.25F)
                    .build("example_projectile"));

    public static void doRegister(IEventBus modBus) {
        REGISTRY.register(modBus);
    }
}
