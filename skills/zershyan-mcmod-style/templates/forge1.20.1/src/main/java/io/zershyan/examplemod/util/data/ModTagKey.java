package io.zershyan.examplemod.util.data;

import io.zershyan.examplemod.ExampleMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;

/** 本 mod 用到的标签键集中声明 */
public final class ModTagKey {

    private ModTagKey() {
    }

    public static final class Items {
        public static final TagKey<Item> EXAMPLE_ITEMS = create(ExampleMod.id("example_items"));

        private Items() {
        }

        public static TagKey<Item> create(final ResourceLocation name) {
            return TagKey.create(Registries.ITEM, name);
        }
    }

    public static final class Blocks {
        public static final TagKey<Block> EXAMPLE_BLOCKS = create(ExampleMod.id("example_blocks"));

        private Blocks() {
        }

        public static TagKey<Block> create(final ResourceLocation name) {
            return TagKey.create(Registries.BLOCK, name);
        }
    }
}
