package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.lang.ExampleModLang;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.RangedAttribute;
import net.minecraftforge.event.entity.EntityAttributeModificationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ExampleModAttributes {
    public static final DeferredRegister<Attribute> REGISTRY =
            DeferredRegister.create(ForgeRegistries.ATTRIBUTES, ExampleMod.MODID);

    public static final RegistryObject<Attribute> EXAMPLE_ABILITY =
            attributeRegister("example_ability", 1, 0, Integer.MAX_VALUE);

    private static RegistryObject<Attribute> attributeRegister(String name, double defaultValue, double min, double max) {
        return REGISTRY.register(name, () -> new RangedAttribute(
                ExampleModLang.getAttributeDesc(ExampleMod.id(name)),
                defaultValue, min, max
        ).setSyncable(true));
    }

    public static void doRegister(IEventBus eventBus) {
        REGISTRY.register(eventBus);
        eventBus.addListener(ExampleModAttributes::attachAttributes);
    }

    public static void attachAttributes(EntityAttributeModificationEvent event) {
        event.add(EntityType.PLAYER, EXAMPLE_ABILITY.get());
    }
}
