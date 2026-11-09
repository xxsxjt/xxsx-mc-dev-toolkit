package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.item.ExampleItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ExampleModItems {
    public static final DeferredRegister<Item> REGISTER =
            DeferredRegister.create(ForgeRegistries.ITEMS, ExampleMod.MODID);
    /** 方块对应的 BlockItem 单独一个注册表，避免与普通物品混在一起 */
    public static final DeferredRegister<Item> BLOCK_ITEM_REGISTER =
            DeferredRegister.create(ForgeRegistries.ITEMS, ExampleMod.MODID);

    public static final RegistryObject<Item> EXAMPLE_ITEM =
            REGISTER.register("example_item", () -> new Item(new Item.Properties()));
    public static final RegistryObject<Item> EXAMPLE_CUSTOM_ITEM =
            REGISTER.register("example_custom_item", ExampleItem::new);

    public static final RegistryObject<BlockItem> EXAMPLE_BLOCK_ITEM =
            BLOCK_ITEM_REGISTER.register("example_block", () -> new BlockItem(ExampleModBlocks.EXAMPLE_BLOCK.get(), new Item.Properties()));
    public static final RegistryObject<BlockItem> EXAMPLE_CUSTOM_BLOCK_ITEM =
            BLOCK_ITEM_REGISTER.register("example_custom_block", () -> new BlockItem(ExampleModBlocks.EXAMPLE_CUSTOM_BLOCK.get(), new Item.Properties()));

    public static void doRegister(IEventBus modBus) {
        REGISTER.register(modBus);
        BLOCK_ITEM_REGISTER.register(modBus);
    }
}
