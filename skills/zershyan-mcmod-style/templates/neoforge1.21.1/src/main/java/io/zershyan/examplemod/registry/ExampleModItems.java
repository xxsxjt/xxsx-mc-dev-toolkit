package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.item.ExampleItem;
import net.minecraft.world.item.Item;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ExampleModItems {
    public static final DeferredRegister.Items REGISTER = DeferredRegister.createItems(ExampleMod.MODID);

    public static final DeferredItem<Item> EXAMPLE_ITEM = REGISTER.register("example_item", () -> new Item(new Item.Properties()));
    public static final DeferredItem<Item> EXAMPLE_CUSTOM_ITEM = REGISTER.register("example_custom_item", ExampleItem::new);

    public static void doRegister(IEventBus modBus) {
        REGISTER.register(modBus);
    }
}
