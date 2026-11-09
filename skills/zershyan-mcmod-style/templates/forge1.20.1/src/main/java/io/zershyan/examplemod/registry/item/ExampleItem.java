package io.zershyan.examplemod.registry.item;

import io.zershyan.examplemod.datagen.lang.ExampleModKeyLang;
import io.zershyan.examplemod.util.ExampleUtil;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class ExampleItem extends Item {
    public ExampleItem() {
        super(new Item.Properties());
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(ExampleModKeyLang.ItemExampleDesc);
        tooltip.add(ExampleModKeyLang.ItemValue.get(ExampleUtil.getValue(stack)));
    }
}
