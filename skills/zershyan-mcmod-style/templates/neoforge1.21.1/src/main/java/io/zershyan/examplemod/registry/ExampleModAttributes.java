package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.lang.ExampleModLang;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.RangedAttribute;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.entity.EntityAttributeModificationEvent;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ExampleModAttributes {
    public static final DeferredRegister<Attribute> REGISTER = DeferredRegister.create(Registries.ATTRIBUTE, ExampleMod.MODID);

    public static final Holder<Attribute> EXAMPLE_ABILITY = attributeRegister("example_ability", 1, 0, Integer.MAX_VALUE);

    public static Holder<Attribute> attributeRegister(String name, double defaultValue, double min, double max) {
        return REGISTER.register(name, location -> new RangedAttribute(
                ExampleModLang.getAttributeDesc(location),
                defaultValue, min, max
        ).setSyncable(true));
    }

    public static void doRegister(IEventBus eventBus) {
        REGISTER.register(eventBus);
        eventBus.addListener(ExampleModAttributes::attachAttributes);
    }

    public static void attachAttributes(EntityAttributeModificationEvent event) {
        event.add(EntityType.PLAYER, EXAMPLE_ABILITY);
    }
}
