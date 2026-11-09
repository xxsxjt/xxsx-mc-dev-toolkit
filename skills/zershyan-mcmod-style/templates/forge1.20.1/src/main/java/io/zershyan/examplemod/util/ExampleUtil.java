package io.zershyan.examplemod.util;

import io.zershyan.examplemod.ExampleMod;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;

public class ExampleUtil {
    private static final String VALUE_KEY = "value";

    public static int getValue(ItemStack stack) {
        CompoundTag tag = stack.getTagElement(ExampleMod.MODID);
        return tag == null ? 0 : tag.getInt(VALUE_KEY);
    }

    public static void setValue(ItemStack stack, int value) {
        stack.getOrCreateTagElement(ExampleMod.MODID).putInt(VALUE_KEY, value);
    }
}
